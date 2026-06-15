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
    pass