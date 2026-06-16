"""
Argos — News Agent
Collects news signals from Google News RSS and Bing News RSS.
"""

import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

import feedparser

from app.config import HIGH_IMPORTANCE_KEYWORDS
from app.signals.registry import SignalSubtype

logger = logging.getLogger(__name__)


class NewsAgent:
    """Collects news signals from Google News and Bing News RSS feeds."""

    def collect(self, keywords: list[str], company_name: str, company_id: str) -> list[dict]:
        """
        Fetch recent news articles matching keywords from
        Google News and Bing News RSS feeds.
        """
        if not keywords:
            return []

        signals = []
        seen_urls = set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        for keyword in keywords:
            query = quote_plus(keyword)

            # ── Google News RSS ─────────────────────────────
            google_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN"
            try:
                feed = feedparser.parse(google_url)
                for entry in feed.entries[:15]:
                    url = entry.get("link", "")
                    if url in seen_urls:
                        continue

                    # Check publish date
                    pub_date = self._parse_date(entry)
                    if pub_date and pub_date < cutoff:
                        continue

                    title = entry.get("title", "")
                    description = entry.get("summary", entry.get("description", ""))

                    importance = self._check_importance(title, description)

                    signals.append({
                        "company_id": company_id,
                        "company_name": company_name,
                        "source": "news",
                        "signal_type": "NEWS",
                        "subtype": "GENERAL_NEWS",
                        "title": title[:300],
                        "content": description[:1000],
                        "url": url,
                        "raw_data": {
                            "source_feed": "google_news",
                            "keyword": keyword,
                            "published": pub_date.isoformat() if pub_date else None,
                        },
                        "importance": importance,
                        "agent": "NewsAgent",
                        "extraction_model": "heuristic"
                    })
                    seen_urls.add(url)
            except Exception as e:
                logger.error(f"Google News error for '{keyword}': {e}")

            # ── Bing News RSS ───────────────────────────────
            bing_url = f"https://www.bing.com/news/search?q={query}&format=rss"
            try:
                feed = feedparser.parse(bing_url)
                for entry in feed.entries[:15]:
                    url = entry.get("link", "")
                    if url in seen_urls:
                        continue

                    pub_date = self._parse_date(entry)
                    if pub_date and pub_date < cutoff:
                        continue

                    title = entry.get("title", "")
                    description = entry.get("summary", entry.get("description", ""))

                    importance = self._check_importance(title, description)

                    signals.append({
                        "company_id": company_id,
                        "company_name": company_name,
                        "source": "news",
                        "signal_type": "NEWS",
                        "subtype": SignalSubtype.GENERAL_NEWS.value,
                        "title": title[:300],
                        "content": description[:1000],
                        "url": url,
                        "raw_data": {
                            "source_feed": "bing_news",
                            "keyword": keyword,
                            "published": pub_date.isoformat() if pub_date else None,
                        },
                        "importance": importance,
                        "agent": "NewsAgent",
                        "extraction_model": "heuristic"
                    })
                    seen_urls.add(url)
            except Exception as e:
                logger.error(f"Bing News error for '{keyword}': {e}")

        logger.info(f"NewsAgent collected {len(signals)} signals for {company_name}")
        return signals

    def _parse_date(self, entry) -> datetime | None:
        """Parse publication date from a feed entry."""
        date_str = entry.get("published", entry.get("updated", ""))
        if not date_str:
            return None
        try:
            parsed = feedparser._parse_date(date_str)
            if parsed:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass

        # Try common formats
        for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None

    def _check_importance(self, title: str, description: str) -> str:
        """Check if title or description contains high-importance keywords."""
        text = f"{title} {description}".lower()
        for keyword in HIGH_IMPORTANCE_KEYWORDS:
            if keyword.lower() in text:
                return "high"
        return "medium"