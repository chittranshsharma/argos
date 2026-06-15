"""
Argos — GitHub Agent
Collects repository metrics and derives engineering velocity intelligence.
"""

import logging
from datetime import datetime, timezone, timedelta
import requests
import json
import re

from app.signals.registry import SignalType, SignalSubtype
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json"}
