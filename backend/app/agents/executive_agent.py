"""
Argos — Executive Agent
Executes high-intent boolean queries to detect and classify executive movements.
Uses LLM to strictly subtype events into the registry enums.
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

class ExecutiveAgent:
    pass