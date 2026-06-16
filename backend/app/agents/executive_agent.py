"""
Argos — Executive Agent
Executes high-intent boolean queries to detect and classify executive movements.
Uses LLM to strictly subtype events into the registry enums.
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

class ExecutiveAgent:
    """Collects executive and leadership movement signals."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """Fetch and extract executive movements."""
        signals = []
        
        # High-intent boolean query
        query = f'"{company_name}" AND ("CEO" OR "CFO" OR "CTO" OR "COO" OR "CRO" OR "board of directors") AND ("steps down" OR "appointed" OR "resigns" OR "hired" OR "joins" OR "leaves")'
        url_encoded_query = quote_plus(query)
        
        articles = []
        seen_urls = set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)

        # Scrape Google News
        google_url = f"https://news.google.com/rss/search?q={url_encoded_query}&hl=en-US&gl=US"
        try:
            feed = feedparser.parse(google_url)
            for entry in feed.entries[:10]:
                url = entry.get("link", "")
                if url in seen_urls: continue
                seen_urls.add(url)
                
                pub_date = self._parse_date(entry)
                if pub_date and pub_date < cutoff: continue
                
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "url": url,
                    "published": pub_date.isoformat() if pub_date else None
                })
        except Exception as e:
            logger.error(f"ExecutiveAgent Google News error: {e}")

        if not articles:
            return []

        # Analyze with LLM
        extracted_events = self._extract_executive_events(articles[:3], company_name)
        
        for event in extracted_events:
            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.EXECUTIVE,
                "subtype": event.get("subtype"),
                "title": event.get("title", "Executive Movement"),
                "content": event.get("content", ""),
                "url": event.get("url", articles[0]["url"]),  # Map back to source URL
                "raw_source_text": event.get("raw_text", ""), # For the sources table
                "payload": {
                    "person": event.get("person"),
                    "role": event.get("role")
                },
                "agent": "ExecutiveAgent",
                "extraction_model": "groq-llama-3"
            })

        logger.info(f"ExecutiveAgent collected {len(signals)} structured signals for {company_name}")
        return signals

    def _extract_executive_events(self, articles: list[dict], company_name: str) -> list[dict]:
        """Use LLM to identify and structure executive movements."""
        articles_text = "\n\n".join([f"URL: {a['url']}\nTITLE: {a['title']}\nDESC: {a['description']}" for a in articles])
        
        prompt = f"""Analyze the following news articles about {company_name}.
Extract any major executive movements (CEO, CTO, CFO, Board).

Allowed Subtypes: CEO_APPOINTED, CEO_DEPARTED, CTO_APPOINTED, CTO_DEPARTED, CFO_APPOINTED, CFO_DEPARTED, COO_APPOINTED, COO_DEPARTED, CRO_APPOINTED, CRO_DEPARTED, BOARD_CHANGE

Articles:
{articles_text}

Return ONLY valid JSON like:
[{{
    "subtype": "CEO_DEPARTED",
    "title": "John Doe steps down as CEO",
    "content": "John Doe has resigned from his position as CEO after 5 years.",
    "url": "https://...",
    "raw_text": "<copy the original article text/description here>",
    "person": "John Doe",
    "role": "CEO"
}}]
If no events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception as e:
            logger.error(f"ExecutiveAgent LLM extraction failed: {e}")
            return []

    def _parse_date(self, entry) -> datetime | None:
        date_str = entry.get("published", entry.get("updated", ""))
        if not date_str: return None
        try:
            parsed = feedparser._parse_date(date_str)
            if parsed: return datetime(*parsed[:6], tzinfo=timezone.utc)
        except: pass
        return None