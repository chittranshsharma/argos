"""
Argos — News Agent
Collects news signals from Google News RSS and Bing News RSS.
"""

import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

import feedparser

from app.config import HIGH_IMPORTANCE_KEYWORDS

logger = logging.getLogger(__name__)


class NewsAgent:
    pass