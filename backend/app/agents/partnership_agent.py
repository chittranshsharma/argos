"""
Argos — Partnerships Agent
Executes high-intent boolean queries to detect strategic alliances and contracts.
Uses NewsAPI (with Google News fallback) and full HTML parsing.

Sprint E.1: Self-partnership rejection, entity normalization, canonical storage.
"""

import logging
import json
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus
import feedparser
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

from app.signals.registry import SignalType
from app.llm import get_groq_llm, llm_invoke
from app.config import NEWSAPI_KEY
from app.memory.graph_db import GraphDB

logger = logging.getLogger(__name__)

# ── Entity Normalization Map ──────────────────────────────────
# Canonical form -> list of known aliases (all lowercased)
ENTITY_ALIASES: dict[str, list[str]] = {
    "AWS": ["amazon web services", "aws", "amazon aws", "amazon cloud"],
    "Microsoft Azure": ["microsoft azure", "azure", "ms azure"],
    "Google Cloud": ["google cloud", "google cloud platform", "gcp", "google cloud services"],
    "SoftBank": ["softbank corp", "softbank group", "softbank corporation", "soft bank"],
    "Google": ["google llc", "alphabet", "alphabet inc"],
    "Meta": ["meta platforms", "facebook", "meta inc"],
    "Salesforce": ["salesforce.com", "salesforce crm", "sfdc"],
    "ServiceNow": ["servicenow inc", "service now"],
    "Deloitte": ["deloitte consulting", "deloitte consulting llp", "deloitte llp"],
    "Microsoft": ["microsoft corp", "microsoft corporation", "msft"],
    "NVIDIA": ["nvidia corp", "nvidia corporation"],
    "SAP": ["sap se", "sap ag"],
    "Palantir": ["palantir technologies", "palantir tech"],
    "Snowflake": ["snowflake inc", "snowflake computing"],
    "LangChain": ["langchain inc", "lang chain"],
    "Weights & Biases": ["weights and biases", "wandb", "w&b"],
    "LatentView Analytics": ["latentview", "latent view analytics"],
    "Visa": ["visa inc", "visa international"],
    "Databricks": ["databricks inc"],
    "Stripe": ["stripe inc", "stripe payments"],
    "Anthropic": ["anthropic pbc", "anthropic ai"],
    "OpenAI": ["openai inc", "openai llc"],
    "Menlo Ventures": ["menlo ventures fund"],
}

# Reverse lookup: alias -> canonical
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in ENTITY_ALIASES.items():
    _ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        _ALIAS_TO_CANONICAL[alias.lower()] = canonical


def normalize_partner(raw_name: str) -> tuple[str, bool]:
    """
    Normalize a raw partner name to its canonical form.
    Returns (canonical_name, was_normalized).
    """
    if not raw_name:
        return raw_name, False
    key = raw_name.strip().lower()
    canonical = _ALIAS_TO_CANONICAL.get(key)
    if canonical:
        return canonical, (canonical.lower() != key)
    # Partial match fallback
    for alias, canon in _ALIAS_TO_CANONICAL.items():
        if alias in key or key in alias:
            return canon, True
    return raw_name.strip(), False


def is_self_reference(company_name: str, partner_name: str) -> bool:
    """Return True if partner is effectively the same entity as the company."""
    if not company_name or not partner_name:
        return True
    c = company_name.strip().lower()
    p = partner_name.strip().lower()
    # Exact or contained
    if c == p or c in p or p in c:
        return True
    # Canonical normalization match
    c_canon, _ = normalize_partner(company_name)
    p_canon, _ = normalize_partner(partner_name)
    if c_canon.lower() == p_canon.lower():
        return True
    return False


class PartnershipsAgent:
    """Collects strategic partnership and contract signals."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """Fetch and extract partnership events with normalization and deduplication."""
        articles = self._fetch_articles(company_name)
        if not articles or not self._check_relevance(articles, company_name):
            return []

        # Batch extraction engine
        raw_events = []
        batch_texts = []
        for article in articles:
            html = self._fetch_html(article["url"])
            paragraphs = self._extract_relevant_paragraphs(html, company_name) if html else ""
            if not paragraphs:
                paragraphs = f"{article.get('title', '')}\n{article.get('description', '')}"
            if len(paragraphs.strip()) < 30:
                continue

            block = f"[URL: {article['url']}]\n{paragraphs.strip()}"
            batch_texts.append(block)

        if batch_texts:
            combined_text = "\n\n".join(batch_texts)
            events = self._extract_partnership_events(combined_text, company_name)
            raw_events.extend(events)

        # ── Normalization & filtering ──────────────────────────
        self_refs_removed = 0
        duplicates_collapsed = 0
        raw_partner_names = []
        normalized_names = []

        dedup_map = defaultdict(list)
        for event in raw_events:
            raw_partner = event.get("partner_name", "").strip()
            raw_partner_names.append(raw_partner)

            # Reject self-partnerships
            if is_self_reference(company_name, raw_partner):
                self_refs_removed += 1
                logger.info(f"[SELF-REF] Rejected: {company_name} -> {raw_partner}")
                continue

            canonical, was_normalized = normalize_partner(raw_partner)
            normalized_names.append(canonical)
            event["partner_name"] = canonical
            event["partner_name_raw"] = raw_partner
            event["partner_was_normalized"] = was_normalized

            subtype = event.get("subtype", "").upper().strip()
            if not subtype or not canonical:
                continue

            key = f"{company_name.lower()}_{subtype}_{canonical.lower()}"
            dedup_map[key].append(event)

        for key, events in dedup_map.items():
            if len(events) > 1:
                duplicates_collapsed += len(events) - 1

        # ── Build signals from deduplicated map ───────────────
        signals = []
        graph_db = GraphDB()

        for key, events in dedup_map.items():
            base_event = events[0]
            source_count = len(events)
            source_urls = list(set(e.get("url") for e in events if e.get("url")))

            payload = {
                "subtype": base_event.get("subtype"),
                "partner_name": base_event.get("partner_name"),
                "partner_name_raw": base_event.get("partner_name_raw"),
                "partner_was_normalized": base_event.get("partner_was_normalized"),
                "partnership_type": base_event.get("subtype"),
                "estimated_value": base_event.get("estimated_value"),
                "industry": base_event.get("industry"),
                "duration": base_event.get("duration"),
                "announcement_date": base_event.get(
                    "announcement_date",
                    datetime.now(timezone.utc).isoformat()[:10]
                ),
                "evidence_url": base_event.get("url"),
                "source_urls": source_urls,
                "source_count": source_count
            }

            # Graph edge with canonical partner
            partner_name = payload["partner_name"]
            graph_db.merge_relationship(
                source=company_name,
                relation="PARTNERS_WITH",
                target=partner_name,
                company_name=company_name
            )

            # Confidence
            from app.analysis.reliability import calculate_weighted_confidence
            extraction_score = 0.9 if payload.get("estimated_value") else 0.75
            evidence_score = 0.85 if payload.get("partner_name") else 0.5
            confidence, reasoning = calculate_weighted_confidence(
                source_urls=source_urls,
                source_count=source_count,
                evidence_score=evidence_score,
                extraction_score=extraction_score
            )
            payload["confidence"] = confidence
            payload["confidence_reasoning"] = reasoning

            subtype_display = str(payload.get("subtype", "")).replace("_", " ").title()
            title = f"{company_name} entered a {subtype_display} with {partner_name}"

            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.PARTNERSHIP,
                "subtype": payload.get("subtype"),
                "title": title,
                "content": f"Partnership detected: {title}.",
                "url": base_event.get("url"),
                "payload": payload,
                "agent": "PartnershipsAgent",
                "extraction_model": "groq-llama-3",
                "review_status": reasoning["review_status"]
            })

        graph_db.close()

        logger.info(
            f"PartnershipsAgent [{company_name}]: "
            f"{len(raw_events)} raw events → "
            f"{self_refs_removed} self-refs removed → "
            f"{duplicates_collapsed} duplicates collapsed → "
            f"{len(signals)} final signals"
        )

        # Attach normalization stats to first signal for reporting
        if signals:
            signals[0]["_stats"] = {
                "raw_count": len(raw_events),
                "self_refs_removed": self_refs_removed,
                "duplicates_collapsed": duplicates_collapsed,
                "final_count": len(signals),
                "raw_partner_names": raw_partner_names,
                "normalized_partner_names": normalized_names,
            }

        return signals

    def _fetch_articles(self, company_name: str) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        if NEWSAPI_KEY:
            query = (
                f'"{company_name}" AND '
                f'("partner" OR "partnership" OR "alliance" OR '
                f'"joint venture" OR "reseller" OR "integration")'
            )
            url = (
                f"https://newsapi.org/v2/everything"
                f"?q={quote_plus(query)}&language=en&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
            )
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = []
                    for a in data.get("articles", [])[:15]:
                        try:
                            pub_date = datetime.strptime(
                                a.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ"
                            ).replace(tzinfo=timezone.utc)
                            if pub_date < cutoff:
                                continue
                        except Exception:
                            pub_date = None
                        articles.append({
                            "title": a.get("title", ""),
                            "description": a.get("description", ""),
                            "url": a.get("url", ""),
                            "published": pub_date
                        })
                    if articles:
                        return articles
            except Exception as e:
                logger.warning(f"NewsAPI failed, falling back to RSS: {e}")

        # Fallback: Google News RSS
        query = (
            f'"{company_name}" AND '
            f'("partner" OR "partnership" OR "alliance" OR "joint venture" OR "integration")'
        )
        google_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US"
        articles = []
        try:
            feed = feedparser.parse(google_url)
            for entry in feed.entries[:15]:
                date_str = entry.get("published", entry.get("updated", ""))
                try:
                    parsed = feedparser._parse_date(date_str)
                    pub_date = datetime(*parsed[:6], tzinfo=timezone.utc) if parsed else None
                except Exception:
                    pub_date = None
                if pub_date and pub_date < cutoff:
                    continue
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "url": entry.get("link", ""),
                    "published": pub_date
                })
        except Exception as e:
            logger.error(f"Google News RSS error: {e}")

        return articles

    def _fetch_html(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                html = resp.text
                if "news.google.com" in url and "c-wiz" in html:
                    match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>', html)
                    if match and match.group(1).startswith("http"):
                        resp = requests.get(match.group(1), headers=headers, timeout=10)
                        if resp.status_code == 200:
                            return resp.text
                return html
        except Exception:
            pass
        return ""

    def _extract_relevant_paragraphs(self, html: str, company_name: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.extract()
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 30]
        terms = ["partner", "alliance", "joint venture", "resell", "integration", "selected", "contract"]
        name_parts = company_name.lower().split()
        relevant = []
        for line in lines:
            ll = line.lower()
            if any(p in ll for p in name_parts) and any(t in ll for t in terms):
                relevant.append(line)
        return "\n".join(relevant[:4])

    def _check_relevance(self, articles: list[dict], company_name: str) -> bool:
        """Evaluate if the article batch contains relevant signals before deep scraping."""
        content = "\n".join([f"{a.get('title', '')} {a.get('description', '')}" for a in articles[:10]]).lower()
        keywords = ["partner", "partnership", "collaboration", "alliance", "agreement", "integration", "joint venture", "reseller"]
        name_parts = company_name.lower().split()
        
        has_company = any(part in content for part in name_parts)
        has_keyword = any(kw in content for kw in keywords)
        
        return has_company and has_keyword

    def _extract_partnership_events(self, text: str, company_name: str) -> list[dict]:
        if len(text.strip()) < 50:
            return []

        prompt = f"""Analyze the following texts from news articles about {company_name}.
Extract any strategic partnerships, cloud alliances, distribution agreements, integrations, joint ventures, or reseller relationships.

CRITICAL RULE: Only extract real external partnerships. Do not extract the company partnering with itself.
Each article text starts with [URL: <url>]. You MUST include the exact URL corresponding to the extracted event in the "url" field.

Allowed Subtypes: STRATEGIC_PARTNERSHIP, CLOUD_PARTNERSHIP, DISTRIBUTION_PARTNERSHIP, TECHNOLOGY_INTEGRATION, JOINT_VENTURE, RESELLER, AI_PARTNERSHIP, GOVERNMENT_CONTRACT

Text Batch:
{text}

Return ONLY valid JSON like:
[{{
    "subtype": "CLOUD_PARTNERSHIP",
    "partner_name": "Microsoft Azure",
    "estimated_value": "$1B",
    "industry": "Cloud Computing",
    "duration": "multi-year",
    "announcement_date": "2024-03-01",
    "url": "https://example.com/article"
}}]
If no events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                events = json.loads(match.group())
                valid_events = []
                allowed_subtypes = {
                    "STRATEGIC_PARTNERSHIP", "CLOUD_PARTNERSHIP", "DISTRIBUTION_PARTNERSHIP",
                    "TECHNOLOGY_INTEGRATION", "JOINT_VENTURE", "RESELLER",
                    "AI_PARTNERSHIP", "GOVERNMENT_CONTRACT"
                }
                for e in events:
                    subtype = e.get("subtype", "").upper().strip()
                    if subtype not in allowed_subtypes:
                        continue
                    if not e.get("partner_name"):
                        continue
                    valid_events.append(e)
                return valid_events
            return []
        except Exception as e:
            logger.error(f"PartnershipAgent LLM extraction failed: {e}")
            return []