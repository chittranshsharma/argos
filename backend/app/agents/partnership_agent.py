"""
Argos — Partnerships Agent
Executes high-intent boolean queries to detect strategic alliances and contracts.
Uses LLM to strictly subtype events and extract partner details and estimated values.
"""

import logging
import json
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus
import feedparser

from app.signals.registry import SignalType, SignalSubtype
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

class PartnershipsAgent:
    """Collects strategic partnership and contract signals."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """Fetch and extract partnership events."""
        signals = []
        
        # High-intent boolean query
        query = f'"{company_name}" AND ("partners with" OR "partnership" OR "strategic alliance" OR "government contract" OR "cloud alliance" OR "selected by")'
        url_encoded_query = quote_plus(query)
        
        articles = []
        seen_urls = set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        # Scrape Google News
        google_url = f"https://news.google.com/rss/search?q={url_encoded_query}&hl=en-US&gl=US"
        try:
            feed = feedparser.parse(google_url)
            for entry in feed.entries[:10]:
                url = entry.get("link", "")
                if url in seen_urls: continue
                seen_urls.add(url)
                
                date_str = entry.get("published", entry.get("updated", ""))
                try:
                    pub_date = feedparser._parse_date(date_str)
                    pub_dt = datetime(*pub_date[:6], tzinfo=timezone.utc) if pub_date else None
                except: pub_dt = None
                
                if pub_dt and pub_dt < cutoff: continue
                
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "url": url
                })
        except Exception as e:
            logger.error(f"PartnershipsAgent Google News error: {e}")

        if not articles:
            return []

        # Analyze with LLM
        extracted_events = self._extract_partnership_events(articles[:3], company_name)
        
        for event in extracted_events:
            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.PARTNERSHIP,
                "subtype": event.get("subtype"),
                "title": event.get("title", "Strategic Partnership Detected"),
                "content": event.get("content", ""),
                "url": event.get("url", articles[0]["url"]),
                "raw_source_text": event.get("raw_text", ""),
                "payload": {
                    "estimated_value": event.get("estimated_value"),
                    "partner_name": event.get("partner_name"),
                    "industry": event.get("industry"),
                    "duration": event.get("duration")
                },
                "agent": "PartnershipsAgent",
                "extraction_model": "groq-llama-3"
            })

        logger.info(f"PartnershipsAgent collected {len(signals)} structured signals for {company_name}")
        return signals

    def _extract_partnership_events(self, articles: list[dict], company_name: str) -> list[dict]:
        """Use LLM to structure partnership events."""
        articles_text = "\n\n".join([f"URL: {a['url']}\nTITLE: {a['title']}\nDESC: {a['description']}" for a in articles])
        
        prompt = f"""Analyze the following news articles about {company_name}.
Extract any strategic partnerships, cloud alliances, or government contracts.

Allowed Subtypes: STRATEGIC_PARTNERSHIP, CLOUD_PARTNERSHIP, AI_PARTNERSHIP, GOVERNMENT_CONTRACT

Articles:
{articles_text}

Return ONLY valid JSON like:
[{{
    "subtype": "GOVERNMENT_CONTRACT",
    "title": "Company wins $50M Defense Contract",
    "content": "Company was selected by the DoD for a 5-year modernization contract.",
    "url": "https://...",
    "raw_text": "<copy the original article text/description here>",
    "partner_name": "Department of Defense",
    "estimated_value": "$50M",
    "industry": "Defense",
    "duration": "5 years"
}}]
If no partnership/contract events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception as e:
            logger.error(f"PartnershipsAgent LLM extraction failed: {e}")
            return []