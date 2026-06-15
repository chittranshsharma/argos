"""
Argos — LinkedIn Agent
Scrapes public LinkedIn company pages for recent posts.
Uses Playwright — gracefully handles login walls.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

