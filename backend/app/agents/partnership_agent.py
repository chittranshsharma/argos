"""
Argos — Partnerships Agent
Executes high-intent boolean queries to detect strategic alliances and contracts.
Uses LLM to strictly subtype events and extract partner details and estimated values.
"""

import logging
import json
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus
import feedparser

from app.signals.registry import SignalType, SignalSubtype
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)
