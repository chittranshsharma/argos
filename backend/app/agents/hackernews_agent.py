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
    pass