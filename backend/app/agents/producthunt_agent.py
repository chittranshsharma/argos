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

