"""
Argos — LLM Factory
Groq (llama-3.3-70b) for fast analysis, Gemini (2.5-flash) for reports.
Includes retry logic via tenacity.
"""

import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.config import GROQ_API_KEY, GROQ_MODEL, GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

