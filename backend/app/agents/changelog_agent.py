"""
Argos — Changelog Agent
Scrapes product changelog/blog pages for recent updates.
"""

import logging
import re
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MAJOR_VERSION_PATTERN = re.compile(r"\bv?\d+\.0(?:\.0)?\b", re.IGNORECASE)


class ChangelogAgent:
    """Scrapes changelog/release-notes pages for product updates."""

    def collect(self, changelog_url: str, company_name: str, company_id: str) -> list[dict]:
        """
        Scrape a changelog page using BeautifulSoup,
        extract recent entries from the last 30 days.
        """
        if not changelog_url:
            return []

        signals = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        try:
            resp = requests.get(
                changelog_url,
                headers={"User-Agent": "Argos/1.0 Competitive Intelligence Bot"},
                timeout=20,
            )
            if resp.status_code != 200:
                logger.warning(f"Changelog fetch failed ({resp.status_code}): {changelog_url}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")

            # ── Strategy 1: Look for article/entry containers ─
            entries = self._extract_entries(soup)

            if not entries:
                # ── Strategy 2: Look for headings with dates ──
                entries = self._extract_from_headings(soup)

            for entry in entries:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                content = entry.get("content", "")
                date = entry.get("date")

                # Check for major version releases
                is_major = bool(MAJOR_VERSION_PATTERN.search(title))
                importance = "high" if is_major else "medium"

                signals.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "source": "changelog",
                    "signal_type": "product_update",
                    "title": title[:300],
                    "content": content[:1000],
                    "url": changelog_url,
                    "raw_data": {
                        "date": date,
                        "is_major_version": is_major,
                    },
                    "importance": importance,
                })

        except requests.RequestException as e:
            logger.error(f"Changelog request error for {changelog_url}: {e}")
        except Exception as e:
            logger.error(f"ChangelogAgent error for {changelog_url}: {e}")

        logger.info(f"ChangelogAgent collected {len(signals)} signals for {company_name}")
        return signals

    def _extract_entries(self, soup: BeautifulSoup) -> list[dict]:
        """Try to extract entries from common changelog patterns."""
        entries = []

        # Look for <article> tags
        articles = soup.find_all("article")
        if articles:
            for article in articles[:20]:
                title_el = article.find(["h1", "h2", "h3", "h4"])
                title = title_el.get_text(strip=True) if title_el else ""
                content = article.get_text(strip=True)[:500]
                date = self._find_date_in_element(article)
                entries.append({"title": title, "content": content, "date": date})
            return entries

        # Look for divs with common changelog class names
        for cls in ["changelog-entry", "release-note", "update", "post", "entry"]:
            divs = soup.find_all(class_=re.compile(cls, re.IGNORECASE))
            if divs:
                for div in divs[:20]:
                    title_el = div.find(["h1", "h2", "h3", "h4"])
                    title = title_el.get_text(strip=True) if title_el else ""
                    content = div.get_text(strip=True)[:500]
                    date = self._find_date_in_element(div)
                    entries.append({"title": title, "content": content, "date": date})
                return entries

        return entries

    def _extract_from_headings(self, soup: BeautifulSoup) -> list[dict]:
        """Extract entries based on heading structure."""
        entries = []
        headings = soup.find_all(["h2", "h3"])

        for heading in headings[:20]:
            title = heading.get_text(strip=True)
            if not title or len(title) < 3:
                continue

            # Collect content until next heading
            content_parts = []
            sibling = heading.find_next_sibling()
            while sibling and sibling.name not in ["h1", "h2", "h3"]:
                text = sibling.get_text(strip=True)
                if text:
                    content_parts.append(text)
                sibling = sibling.find_next_sibling()
                if len(content_parts) > 5:
                    break

            content = " ".join(content_parts)[:500]
            date = self._find_date_in_element(heading)

            entries.append({"title": title, "content": content, "date": date})

        return entries

    def _find_date_in_element(self, element) -> str | None:
        """Try to find a date string near an element."""
        # Look for <time> tags
        time_el = element.find("time")
        if time_el:
            return time_el.get("datetime", time_el.get_text(strip=True))

        # Look for date patterns in text
        text = element.get_text()
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\w+ \d{1,2},? \d{4}",
            r"\d{1,2} \w+ \d{4}",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()

        return None