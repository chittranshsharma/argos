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
    pass