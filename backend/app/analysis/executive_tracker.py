import json
import logging
import re
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

EXECUTIVE_TITLES = [
    "ceo", "cto", "coo", "cfo", "cpo", "vp", "vice president",
    "director", "head of", "chief", "founder", "president",
    "managing director", "md", "svp", "evp", "partner"
]

class ExecutiveTracker:
    pass