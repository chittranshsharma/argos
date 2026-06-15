"""
Argos — Launch Agent
Aggregates product launches and features from ProductHunt and high-intent news queries.
Uses LLM to subtype launches into major products, features, betas, etc.
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

class LaunchAgent:
    """Collects and classifies product launch signals."""

    def collect(self, company_name: str, company_id: str, producthunt_slug: str = None) -> list[dict]:
        """Fetch and extract product launches."""
        signals = []
        articles = []
        seen_urls = set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        
        # 1. High-intent boolean query for News
        query = f'"{company_name}" AND ("launches" OR "announces" OR "unveils" OR "releases" OR "new feature" OR "beta" OR "pricing change")'
        url_encoded_query = quote_plus(query)
        
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
            logger.error(f"LaunchAgent Google News error: {e}")

        # Note: We skip direct ProductHunt GraphQL here for simplicity since the news aggregator 
        # is usually faster and more reliable than a missing slug, but the LLM will structure it identically.
        
        if not articles:
            return []

        # Analyze with LLM
        extracted_events = self._extract_launch_events(articles[:3], company_name)
        
        for event in extracted_events:
            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.LAUNCH,
                "subtype": event.get("subtype"),
                "title": event.get("title", "Product Launch Detected"),
                "content": event.get("content", ""),
                "url": event.get("url", articles[0]["url"]),
                "raw_source_text": event.get("raw_text", ""),
                "payload": {
                    "product": event.get("product"),
                    "impact_score": event.get("impact_score", 5.0)
                },
                "agent": "LaunchAgent",
                "extraction_model": "groq-llama-3"
            })

        logger.info(f"LaunchAgent collected {len(signals)} structured signals for {company_name}")
        return signals

    def _extract_launch_events(self, articles: list[dict], company_name: str) -> list[dict]:
        """Use LLM to structure launch events."""
        articles_text = "\n\n".join([f"URL: {a['url']}\nTITLE: {a['title']}\nDESC: {a['description']}" for a in articles])
        
        prompt = f"""Analyze the following news articles about {company_name}.
Extract any product launches, feature releases, or major beta announcements.

Allowed Subtypes: MAJOR_PRODUCT, MAJOR_FEATURE, BETA, INTEGRATION, PRICING_CHANGE

Articles:
{articles_text}

Return ONLY valid JSON like:
[{{
    "subtype": "MAJOR_FEATURE",
    "title": "Company releases new AI Copilot",
    "content": "Company announced a new AI Copilot feature for their core platform.",
    "url": "https://...",
    "raw_text": "<copy the original article text/description here>",
    "product": "AI Copilot",
    "impact_score": 8.5
}}]
If no product launch events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception as e:
            logger.error(f"LaunchAgent LLM extraction failed: {e}")
            return []