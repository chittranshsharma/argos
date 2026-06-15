"""
Argos — ProductHunt Agent
Collects recent launches and updates from ProductHunt GraphQL API.
"""

import logging
from datetime import datetime, timezone, timedelta

import requests

from app.config import PRODUCTHUNT_DEVELOPER_TOKEN

logger = logging.getLogger(__name__)

PH_API_URL = "https://api.producthunt.com/v2/api/graphql"


class ProductHuntAgent:
    """Collects signals from ProductHunt product launches."""

    def collect(self, slug: str, company_name: str, company_id: str) -> list[dict]:
        """
        Query ProductHunt GraphQL API for recent posts by a maker/product.
        All ProductHunt launches are marked as high importance.
        """
        if not slug or not PRODUCTHUNT_DEVELOPER_TOKEN:
            return []

        signals = []

        try:
            headers = {
                "Authorization": f"Bearer {PRODUCTHUNT_DEVELOPER_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            # ── Query for posts by topic/slug ───────────────
            query = """
            query ($slug: String!) {
                topic(slug: $slug) {
                    posts(first: 10, order: NEWEST) {
                        edges {
                            node {
                                id
                                name
                                tagline
                                description
                                url
                                votesCount
                                commentsCount
                                createdAt
                                website
                                makers {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """

            payload = {
                "query": query,
                "variables": {"slug": slug},
            }

            resp = requests.post(PH_API_URL, json=payload, headers=headers, timeout=15)

            if resp.status_code != 200:
                logger.warning(f"ProductHunt API returned {resp.status_code}")
                # Try alternative: search by name
                return self._search_by_name(company_name, company_id, headers)

            data = resp.json()
            posts_data = data.get("data", {}).get("topic", {})

            if not posts_data:
                # Topic not found, try search
                return self._search_by_name(company_name, company_id, headers)

            edges = posts_data.get("posts", {}).get("edges", [])

            cutoff = datetime.now(timezone.utc) - timedelta(days=30)

            for edge in edges:
                node = edge.get("node", {})
                created_at = node.get("createdAt", "")

                try:
                    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if created_dt < cutoff:
                        continue
                except (ValueError, TypeError):
                    pass

                makers = ", ".join(m.get("name", "") for m in node.get("makers", []))

                signals.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "source": "producthunt",
                    "signal_type": "launch",
                    "title": f"ProductHunt: {node.get('name', '')} — {node.get('tagline', '')}",
                    "content": node.get("description", "")[:1000],
                    "url": node.get("url", ""),
                    "raw_data": {
                        "votes": node.get("votesCount", 0),
                        "comments": node.get("commentsCount", 0),
                        "website": node.get("website", ""),
                        "makers": makers,
                    },
                    "importance": "high",  # All PH launches are high importance
                })

        except requests.RequestException as e:
            logger.error(f"ProductHunt API error: {e}")
        except Exception as e:
            logger.error(f"ProductHuntAgent unexpected error: {e}")

        logger.info(f"ProductHuntAgent collected {len(signals)} signals for {company_name}")
        return signals

    def _search_by_name(self, company_name: str, company_id: str, headers: dict) -> list[dict]:
        """Fallback: search ProductHunt by company name."""
        signals = []

        query = """
        query ($query: String!) {
            posts(first: 10, order: RANKING, topic: $query) {
                edges {
                    node {
                        id
                        name
                        tagline
                        url
                        votesCount
                        createdAt
                    }
                }
            }
        }
        """

        try:
            payload = {"query": query, "variables": {"query": company_name}}
            resp = requests.post(PH_API_URL, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                edges = data.get("data", {}).get("posts", {}).get("edges", [])
                for edge in edges:
                    node = edge.get("node", {})
                    if company_name.lower() in node.get("name", "").lower():
                        signals.append({
                            "company_id": company_id,
                            "company_name": company_name,
                            "source": "producthunt",
                            "signal_type": "launch",
                            "title": f"ProductHunt: {node.get('name', '')} — {node.get('tagline', '')}",
                            "content": "",
                            "url": node.get("url", ""),
                            "raw_data": {"votes": node.get("votesCount", 0)},
                            "importance": "high",
                        })
        except Exception as e:
            logger.error(f"ProductHunt search fallback error: {e}")

        return signals