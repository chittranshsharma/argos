"""
Argos — Hacker News Agent
Collects mentions from Hacker News using the Algolia API (free, no key).
"""

import logging
from datetime import datetime, timezone, timedelta

import requests

logger = logging.getLogger(__name__)

HN_ALGOLIA_API = "https://hn.algolia.com/api/v1"


class HackerNewsAgent:
    """Collects signals from Hacker News via Algolia search API."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """
        Search Hacker News for mentions of a company name.
        Uses the Algolia HN API (free, no API key required).
        """
        if not company_name:
            return []

        signals = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        cutoff_ts = int(cutoff.timestamp())

        try:
            # ── Search stories ──────────────────────────────
            url = f"{HN_ALGOLIA_API}/search"
            params = {
                "query": company_name,
                "tags": "story",
                "numericFilters": f"created_at_i>{cutoff_ts}",
                "hitsPerPage": 30,
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"HN API returned {resp.status_code}")
                return []

            data = resp.json()
            hits = data.get("hits", [])

            for hit in hits:
                title = hit.get("title", "")
                story_url = hit.get("url", "")
                hn_url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                points = hit.get("points", 0) or 0
                num_comments = hit.get("num_comments", 0) or 0

                # Determine signal type
                if title.lower().startswith("ask hn"):
                    signal_type = "ask_hn"
                elif title.lower().startswith("show hn"):
                    signal_type = "show_hn"
                else:
                    signal_type = "mention"

                # High importance if > 50 points
                importance = "high" if points > 50 else "medium"

                created_at = hit.get("created_at", "")

                signals.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "source": "hackernews",
                    "signal_type": "SOCIAL",
                    "subtype": "HACKER_NEWS",
                    "title": title[:300],
                    "content": f"Points: {points}, Comments: {num_comments}. {story_url}",
                    "url": hn_url,
                    "raw_data": {
                        "points": points,
                        "num_comments": num_comments,
                        "author": hit.get("author", ""),
                        "story_url": story_url,
                        "created_at": created_at,
                    },
                    "importance": importance,
                    "agent": "HackerNewsAgent",
                    "extraction_model": "heuristic"
                })

        except requests.RequestException as e:
            logger.error(f"HN API error for {company_name}: {e}")
        except Exception as e:
            logger.error(f"HackerNewsAgent unexpected error: {e}")

        logger.info(f"HackerNewsAgent collected {len(signals)} signals for {company_name}")
        return signals