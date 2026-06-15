"""
Argos — Funding Agent
Executes high-intent boolean queries to detect funding rounds and M&A events.
Uses LLM to strictly subtype events and extract financial metrics.
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

class FundingAgent:
    """Collects funding and M&A signals."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """Fetch and extract funding events."""
        signals = []
        
        # High-intent boolean query
        query = f'"{company_name}" AND ("raises" OR "funding" OR "series" OR "valuation" OR "acquired" OR "IPO" OR "seed round")'
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
                
                pub_date = self._parse_date(entry)
                if pub_date and pub_date < cutoff: continue
                
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "url": url,
                    "published": pub_date.isoformat() if pub_date else None
                })
        except Exception as e:
            logger.error(f"FundingAgent Google News error: {e}")

        if not articles:
            return []

        # Analyze with LLM
        extracted_events = self._extract_funding_events(articles[:3], company_name)
        
        for event in extracted_events:
            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.FUNDING,
                "subtype": event.get("subtype"),
                "title": event.get("title", f"Funding Event Detected"),
                "content": event.get("content", ""),
                "url": event.get("url", articles[0]["url"]),
                "raw_source_text": event.get("raw_text", ""),
                "payload": {
                    "valuation": event.get("valuation"),
                    "amount": event.get("amount"),
                    "investors": event.get("investors", [])
                },
                "agent": "FundingAgent",
                "extraction_model": "groq-llama-3"
            })

        logger.info(f"FundingAgent collected {len(signals)} structured signals for {company_name}")
        return signals

    def _extract_funding_events(self, articles: list[dict], company_name: str) -> list[dict]:
        """Use LLM to structure funding events."""
        articles_text = "\n\n".join([f"URL: {a['url']}\nTITLE: {a['title']}\nDESC: {a['description']}" for a in articles])
        
        prompt = f"""Analyze the following news articles about {company_name}.
Extract any major funding rounds, acquisitions, or IPOs.

Allowed Subtypes: SEED, SERIES_A, SERIES_B, SERIES_C, IPO, ACQUISITION, DEBT

Articles:
{articles_text}

Return ONLY valid JSON like:
[{{
    "subtype": "SERIES_A",
    "title": "Company raises $20M Series A",
    "content": "Company raised a $20M Series A led by XYZ Capital at a $100M valuation.",
    "url": "https://...",
    "raw_text": "<copy the original article text/description here>",
    "amount": "$20M",
    "valuation": "$100M",
    "investors": ["XYZ Capital", "ABC Ventures"]
}}]
If no funding/M&A events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception as e:
            logger.error(f"FundingAgent LLM extraction failed: {e}")
            return []

    def _parse_date(self, entry) -> datetime | None:
        date_str = entry.get("published", entry.get("updated", ""))
        if not date_str: return None
        try:
            parsed = feedparser._parse_date(date_str)
            if parsed: return datetime(*parsed[:6], tzinfo=timezone.utc)
        except: pass
        return None