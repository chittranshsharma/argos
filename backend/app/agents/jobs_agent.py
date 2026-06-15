"""
Argos — Jobs Agent
Scrapes company careers pages (or ATS APIs) to detect new/removed job postings.
Applies LLM analysis to group jobs into strategic hiring signals.
"""

import logging
import json
import re
import requests
from datetime import datetime, timezone

from app.signals.registry import SignalType, SignalSubtype
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

class JobsAgent:
    pass