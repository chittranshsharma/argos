"""
Argos — Funding Agent
Executes high-intent boolean queries to detect and classify funding and acquisition events.
Uses NewsAPI (with Google News fallback) and full HTML parsing to strictly subtype events.
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
import math

from app.signals.registry import SignalType
from app.llm import get_groq_llm, llm_invoke
from app.config import NEWSAPI_KEY

logger = logging.getLogger(__name__)

class FundingAgent:
    """Collects funding and acquisition signals."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """Fetch and extract funding movements."""
        articles = self._fetch_articles(company_name)
        if not articles or not self._check_relevance(articles, company_name):
            return []

        # Batch extraction engine
        raw_events = []
        batch_texts = []
        for article in articles:
            html = self._fetch_html(article["url"])
            if html:
                paragraphs = self._extract_relevant_paragraphs(html, company_name)
            else:
                paragraphs = ""
            
            # Fallback to article title/description if HTML extraction fails or yields nothing
            if not paragraphs:
                paragraphs = f"{article.get('title', '')}\n{article.get('description', '')}"
                
            if not paragraphs.strip():
                continue
            
            block = f"[URL: {article['url']}]\n{paragraphs.strip()}"
            batch_texts.append(block)

        if batch_texts:
            combined_text = "\n\n".join(batch_texts)
            events = self._extract_funding_events(combined_text, company_name)
            raw_events.extend(events)

        # Deduplicate and aggregate
        dedup_map = defaultdict(list)
        for event in raw_events:
            subtype = event.get("subtype", "").upper().strip()
            amount = event.get("amount", "").lower().strip()
            target = event.get("target_company", "").lower().strip()
            date = event.get("announcement_date", "").lower().strip()
            
            if subtype == "ACQUISITION":
                key = f"{company_name.lower().strip()}_{subtype}_{target}"
            else:
                key = f"{company_name.lower().strip()}_{subtype}_{amount}_{date}"
                
            if not subtype: 
                continue
            dedup_map[key].append(event)
        
        signals = []
        for key, events in dedup_map.items():
            base_event = events[0]
            source_count = len(events)
            source_urls = list(set([e.get("url") for e in events if e.get("url")]))
            
            payload = {
                "subtype": base_event.get("subtype"),
                "amount": base_event.get("amount"),
                "valuation": base_event.get("valuation"),
                "lead_investors": base_event.get("lead_investors", []),
                "round_type": base_event.get("round_type"),
                "target_company": base_event.get("target_company"),
                "announcement_date": base_event.get("announcement_date", datetime.now(timezone.utc).isoformat()[:10]),
                "evidence_url": base_event.get("url"),
                "source_urls": source_urls,
                "source_count": source_count
            }
            
            # --- Graph Persistence ---
            try:
                from app.memory.graph_db import GraphDB
                graph_db = GraphDB()
                if payload.get("subtype") == "ACQUISITION" and payload.get("target_company"):
                    graph_db.merge_relationship(
                        source=company_name,
                        relation="ACQUIRED",
                        target=payload["target_company"].strip(),
                        company_name=company_name
                    )
                elif payload.get("lead_investors"):
                    for inv in payload["lead_investors"]:
                        if isinstance(inv, str) and inv.strip():
                            graph_db.merge_relationship(
                                source=inv.strip(),
                                relation="INVESTED_IN",
                                target=company_name,
                                company_name=company_name
                            )
                graph_db.close()
            except Exception as e:
                logger.error(f"FundingAgent GraphDB update failed: {e}")
            # --------------------------

            # FINAL PERSISTENCE GUARD - SIGNAL VALIDATION V2
            subtype = str(payload.get("subtype", "")).upper()
            has_value_signal = payload.get("amount") or payload.get("valuation") or payload.get("lead_investors") or payload.get("target_company")
            
            if not subtype or not has_value_signal:
                logger.warning(f"FundingAgent rejected signal due to missing subtype or value indicators: {json.dumps(payload)}")
                continue

            # Confidence Calibration
            from app.analysis.reliability import calculate_weighted_confidence
            
            extraction_score = 0.9 if payload.get("amount") and payload.get("round_type") else 0.7
            evidence_score = 0.85 if has_value_signal else 0.5
            
            confidence, reasoning = calculate_weighted_confidence(
                source_urls=source_urls,
                source_count=source_count,
                evidence_score=evidence_score,
                extraction_score=extraction_score
            )
            
            reasoning["value_indicators_detected"] = bool(has_value_signal)
            payload["confidence"] = confidence
            payload["confidence_reasoning"] = reasoning

            title = f"{company_name} "
            if subtype == "ACQUISITION":
                title += "Acquired/Acquisition Event"
            elif subtype == "IPO":
                title += "filed for IPO"
            else:
                title += f"raised {payload.get('amount', 'undisclosed amount')} in {payload.get('round_type', subtype)}"

            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.FUNDING,
                "subtype": subtype,
                "title": title,
                "content": f"Funding event detected: {title}. Investors: {', '.join(payload.get('lead_investors', []))}",
                "url": base_event.get("url"),
                "payload": payload,
                "agent": "FundingAgent",
                "extraction_model": "groq-llama-3",
                "review_status": reasoning["review_status"]
            })
            
        logger.info(f"FundingAgent collected {len(signals)} validated signals for {company_name}")
        return signals

    def _fetch_articles(self, company_name: str) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        
        if NEWSAPI_KEY:
            query = f'"{company_name}" AND ("funding" OR "raised" OR "Series" OR "Seed" OR "Acquisition" OR "Acquired" OR "IPO" OR "Valuation")'
            url = f"https://newsapi.org/v2/everything?q={quote_plus(query)}&language=en&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = []
                    for a in data.get("articles", [])[:10]:
                        try:
                            pub_date = datetime.strptime(a.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            if pub_date < cutoff: continue
                        except: pub_date = None
                        
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
                
        # Fallback to Google News RSS
        query = f'"{company_name}" AND ("funding" OR "raised" OR "Series" OR "Acquisition")'
        url_encoded_query = quote_plus(query)
        google_url = f"https://news.google.com/rss/search?q={url_encoded_query}&hl=en-US&gl=US"
        articles = []
        try:
            feed = feedparser.parse(google_url)
            for entry in feed.entries[:10]:
                date_str = entry.get("published", entry.get("updated", ""))
                try:
                    parsed = feedparser._parse_date(date_str)
                    pub_date = datetime(*parsed[:6], tzinfo=timezone.utc) if parsed else None
                except: pub_date = None
                
                if pub_date and pub_date < cutoff: continue
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
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                html = resp.text
                if "news.google.com" in url and 'c-wiz' in html:
                    match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>', html)
                    if match and match.group(1).startswith("http"):
                        real_url = match.group(1)
                        resp = requests.get(real_url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            return resp.text
                return html
        except Exception:
            pass
        return ""

    def _extract_relevant_paragraphs(self, html: str, company_name: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.extract()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 30]
        
        relevant = []
        funding_terms = ["raised", "funding", "round", "series", "seed", "acquired", "acquisition", "ipo"]
        value_terms = ["million", "billion", "$", "undisclosed"]
        name_parts = company_name.lower().split()
        
        for line in lines:
            line_lower = line.lower()
            has_company = any(part in line_lower for part in name_parts)
            has_funding = any(term in line_lower for term in funding_terms)
            has_value = any(term in line_lower for term in value_terms)
            
            # Score logic: we need company + funding + (optional but heavily weighted) value
            if has_company and has_funding:
                # If they have a value term, they go to the front
                if has_value:
                    relevant.insert(0, line)
                else:
                    relevant.append(line)
                
        # Return only top 3 paragraphs to save tokens and reduce noise
        return "\n".join(relevant[:3])

    def _check_relevance(self, articles: list[dict], company_name: str) -> bool:
        """Evaluate if the article batch contains relevant signals before deep scraping."""
        content = "\n".join([f"{a.get('title', '')} {a.get('description', '')}" for a in articles[:10]]).lower()
        keywords = ["raised", "funding", "series", "seed", "round", "valuation", "investor", "capital", "acquired", "acquisition", "ipo"]
        name_parts = company_name.lower().split()
        
        has_company = any(part in content for part in name_parts)
        has_keyword = any(kw in content for kw in keywords)
        
        return has_company and has_keyword

    def _extract_funding_events(self, text: str, company_name: str) -> list[dict]:
        if len(text.strip()) < 50:
            return []
            
        prompt = f"""Analyze the following texts from news articles about {company_name}.
Extract any major funding, investment, or acquisition events.

CRITICAL RULE: ONLY extract actual funding events (e.g. Series A, Seed, Acquisition, IPO). Do not extract general news or unverified rumors. If no funding event is described, return an empty array [].
Each article text starts with [URL: <url>]. You MUST include the exact URL corresponding to the extracted event in the "url" field.

Allowed Subtypes: SEED, SERIES_A, SERIES_B, SERIES_C, IPO, ACQUISITION, DEBT

Text Batch:
{text}

Return ONLY valid JSON like:
[{{
    "subtype": "SERIES_A",
    "amount": "$50M",
    "valuation": "$500M",
    "lead_investors": ["Sequoia", "a16z"],
    "round_type": "Series A",
    "target_company": "",
    "announcement_date": "October 15, 2023",
    "url": "https://example.com/article"
}}]
If no funding events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                events = json.loads(match.group())
                valid_events = []
                allowed_subtypes = {"SEED", "SERIES_A", "SERIES_B", "SERIES_C", "IPO", "ACQUISITION", "DEBT"}
                for e in events:
                    subtype = e.get("subtype", "").upper().strip()
                    if subtype not in allowed_subtypes:
                        logger.warning({"reason": "invalid_subtype", "llm_output": e})
                        continue
                    
                    has_value_signal = e.get("amount") or e.get("valuation") or e.get("lead_investors") or e.get("target_company")
                    if not has_value_signal:
                        logger.warning({"reason": "missing_value_indicators", "llm_output": e})
                        continue
                    valid_events.append(e)
                return valid_events
            return []
        except Exception as e:
            logger.error(f"FundingAgent LLM extraction failed: {e}")
            return []