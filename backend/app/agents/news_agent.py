"""
Argos — News Agent
Collects news signals from Google News RSS and Bing News RSS.
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus, urlparse

import feedparser

from app.config import HIGH_IMPORTANCE_KEYWORDS
from app.signals.registry import SignalSubtype

logger = logging.getLogger(__name__)


class NewsAgent:
    """Collects news signals from Google News and Bing News RSS feeds."""

    def collect(self, keywords: list[str], company_name: str, company_id: str, website: str = None) -> list[dict]:
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
            # Phase 2: Query Construction
            # Ensure company name is always in the query
            if keyword.lower() == company_name.lower():
                query = quote_plus(f'"{company_name}"')
            else:
                query = quote_plus(f'"{company_name}" {keyword}')

            # ── Google News RSS ─────────────────────────────
            google_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN"
            self._fetch_feed(google_url, "google_news", keyword, company_name, company_id, website, cutoff, seen_urls, signals)
            
            # ── Bing News RSS ───────────────────────────────
            bing_url = f"https://www.bing.com/news/search?q={query}&format=rss"
            self._fetch_feed(bing_url, "bing_news", keyword, company_name, company_id, website, cutoff, seen_urls, signals)

        logger.info(f"NewsAgent {company_name} Audit: Fetched={len(seen_urls)}, Saved={len(signals)}, Discarded={len(seen_urls) - len(signals)}")
        return signals

    def _fetch_feed(self, url_feed: str, source_feed: str, keyword: str, company_name: str, company_id: str, website: str, cutoff: datetime, seen_urls: set, signals: list):
        try:
            feed = feedparser.parse(url_feed)
            for entry in feed.entries[:15]:
                url = entry.get("link", "")
                if url in seen_urls:
                    continue

                seen_urls.add(url)

                pub_date = self._parse_date(entry)
                if pub_date and pub_date < cutoff:
                    continue

                title = entry.get("title", "")
                description = entry.get("summary", entry.get("description", ""))

                # Phase 3: Attribution Gate
                score, matched_rules = self._calculate_attribution_score(title, description, url, company_name, website, keyword)
                
                # Phase 3.5: Audit Logging
                audit_log = {
                    "title": title[:100] + "...",
                    "score": score,
                    "matched_rules": matched_rules,
                    "company": company_name,
                    "keyword": keyword,
                    "url": url
                }

                if score < 3:
                    logger.info(f"NewsAgent Attribution DISCARDED: {audit_log}")
                    continue
                
                logger.info(f"NewsAgent Attribution ACCEPTED: {audit_log}")

                importance = self._check_importance(title, description)

                subtype_val = SignalSubtype.GENERAL_NEWS.value if hasattr(SignalSubtype, "GENERAL_NEWS") else "GENERAL_NEWS"

                signals.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "source": "news",
                    "signal_type": "NEWS",
                    "subtype": subtype_val,
                    "title": title[:300],
                    "content": description[:1000],
                    "url": url,
                    "raw_data": {
                        "source_feed": source_feed,
                        "keyword": keyword,
                        "published": pub_date.isoformat() if pub_date else None,
                        "attribution_score": score,
                        "matched_rules": matched_rules
                    },
                    "importance": importance,
                    "agent": "NewsAgent",
                    "extraction_model": "heuristic"
                })
        except Exception as e:
            logger.error(f"{source_feed} error for '{keyword}': {e}")

    def _calculate_attribution_score(self, title: str, description: str, url: str, company_name: str, website: str, keyword: str) -> tuple[int, list[str]]:
        score = 0
        matched_rules = []
        
        # Phase 4: Stripe Special Case
        if company_name.lower() == "stripe":
            comp_pattern = r'\b[sS]tripe\b'
            in_title = bool(re.search(comp_pattern, title))
            in_desc = bool(re.search(comp_pattern, description))
        else:
            in_title = company_name.lower() in title.lower()
            in_desc = company_name.lower() in description.lower()
            
        if in_title:
            score += 3
            matched_rules.append("company_in_title")
        if in_desc:
            score += 2
            matched_rules.append("company_in_description")
            
        # Domain check
        if website:
            try:
                domain = urlparse(website).netloc.replace("www.", "").lower()
                article_domain = urlparse(url).netloc.replace("www.", "").lower()
                if domain and domain in article_domain:
                    score += 5
                    matched_rules.append("official_domain_present")
            except Exception:
                pass
                
        # Keyword check (product or founder)
        if keyword.lower() != company_name.lower():
            if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                score += 2
                matched_rules.append("product_or_founder_present")
                
        return score, matched_rules

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