"""
Argos — Reddit Agent
Collects mentions and discussions from Reddit using PRAW.
"""

import logging
from datetime import datetime, timezone, timedelta

import praw
from praw.exceptions import PRAWException

from app.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

logger = logging.getLogger(__name__)


class RedditAgent:
    """Collects signals from Reddit: posts and comment spikes."""

    def __init__(self):
        self.reddit = None
        if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
            try:
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT,
                )
            except Exception as e:
                logger.error(f"Failed to initialize PRAW: {e}")

    def collect(self, subreddit: str, company_name: str, company_id: str) -> list[dict]:
        """
        Search for company mentions on Reddit across
        the company subreddit and general startup subreddits.
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized — skipping")
            return []

        signals = []
        seen_urls = set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        # Subreddits to search
        subreddits_to_search = [subreddit] if subreddit else []
        subreddits_to_search.extend(["india", "indianstartups", "startups"])

        for sub_name in subreddits_to_search:
            if not sub_name:
                continue
            try:
                sub = self.reddit.subreddit(sub_name)

                # ── Search for company name ─────────────────
                for post in sub.search(company_name, sort="new", time_filter="week", limit=20):
                    url = f"https://reddit.com{post.permalink}"
                    if url in seen_urls:
                        continue

                    created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    if created < cutoff:
                        continue

                    score = post.score
                    num_comments = post.num_comments
                    importance = "high" if score > 100 else "medium"

                    signals.append({
                        "company_id": company_id,
                        "company_name": company_name,
                        "source": "reddit",
                        "signal_type": "post",
                        "title": post.title[:300],
                        "content": (post.selftext or "")[:1000],
                        "url": url,
                        "raw_data": {
                            "subreddit": sub_name,
                            "score": score,
                            "num_comments": num_comments,
                            "author": str(post.author),
                            "upvote_ratio": post.upvote_ratio,
                        },
                        "importance": importance,
                    })
                    seen_urls.add(url)

                    # Check for comment spikes
                    if num_comments > 50:
                        signals.append({
                            "company_id": company_id,
                            "company_name": company_name,
                            "source": "reddit",
                            "signal_type": "comment_spike",
                            "title": f"High engagement: {post.title[:200]}",
                            "content": f"{num_comments} comments, score {score}",
                            "url": url,
                            "raw_data": {
                                "subreddit": sub_name,
                                "score": score,
                                "num_comments": num_comments,
                            },
                            "importance": "high",
                        })

                # ── Hot posts mentioning company ────────────
                for post in sub.hot(limit=25):
                    if company_name.lower() not in (post.title + (post.selftext or "")).lower():
                        continue
                    url = f"https://reddit.com{post.permalink}"
                    if url in seen_urls:
                        continue

                    created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    if created < cutoff:
                        continue

                    signals.append({
                        "company_id": company_id,
                        "company_name": company_name,
                        "source": "reddit",
                        "signal_type": "post",
                        "title": post.title[:300],
                        "content": (post.selftext or "")[:1000],
                        "url": url,
                        "raw_data": {
                            "subreddit": sub_name,
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "is_hot": True,
                        },
                        "importance": "high" if post.score > 100 else "medium",
                    })
                    seen_urls.add(url)

            except PRAWException as e:
                logger.error(f"Reddit error for r/{sub_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected Reddit error for r/{sub_name}: {e}")

        logger.info(f"RedditAgent collected {len(signals)} signals for {company_name}")
        return signals