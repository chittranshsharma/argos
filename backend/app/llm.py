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


def get_groq_llm(max_tokens: int = 500) -> ChatGroq:
    """Create a Groq LLM instance with llama-3.3-70b-versatile.

    Args:
        max_tokens: Token budget for the response. Validators use the default
                    (500 — enough for a single scored JSON object). The
                    HypothesisEngine uses 2000 to output 5 tensions or
                    hypotheses without truncating mid-JSON.
    """
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.1,
        max_tokens=max_tokens,
    )


def get_gemini_llm() -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance using the configured model."""
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        max_output_tokens=8192,
    )


LLM_STATS = {
    "calls": 0,
    "total_time": 0.0,
    "retries": 0,
    "rate_limits": 0
}

def llm_invoke(llm, prompt: str) -> str:
    """
    Invoke an LLM with retry logic.
    Returns the text content of the response.
    Falls back to Gemini if Groq fails due to rate limits.
    """
    import time
    global LLM_STATS
    LLM_STATS["calls"] += 1
    t0 = time.time()
    
    try:
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=5, max=20),
            retry=retry_if_exception_type(Exception)
        )
        def _invoke_primary():
            try:
                return llm.invoke([HumanMessage(content=prompt)])
            except Exception as e:
                LLM_STATS["retries"] += 1
                if "429" in str(e) or "Too Many Requests" in str(e):
                    LLM_STATS["rate_limits"] += 1
                raise e
            
        response = _invoke_primary()
        LLM_STATS["total_time"] += (time.time() - t0)
        return response.content
    except Exception as e:
        logger.warning(f"Primary LLM failed ({e}). Falling back to Gemini...")
        gemini = get_gemini_llm()
        
        @retry(
            stop=stop_after_attempt(1),
            wait=wait_exponential(multiplier=1, min=1, max=3),
            retry=retry_if_exception_type(Exception)
        )
        def _invoke_fallback():
            import time
            time.sleep(2)
            try:
                return gemini.invoke([HumanMessage(content=prompt)])
            except Exception as e:
                LLM_STATS["retries"] += 1
                raise e
            
        try:
            response = _invoke_fallback()
            LLM_STATS["total_time"] += (time.time() - t0)
            return response.content
        except Exception as e:
            LLM_STATS["total_time"] += (time.time() - t0)
            logger.warning(f"Fallback LLM failed ({e}). Using mock response for testing...")
            if "Executive Summary" in prompt or "key developments" in prompt.lower() or "report" in prompt.lower():
                return "## Intelligence Report Unavailable\n\n### Executive Summary\nDue to LLM API rate limits, the automated summarization engine could not generate a full analysis for this cycle. The system continues to monitor and store raw signals securely.\n\n### Key Signals\n* The system successfully scraped and stored the signals, but could not synthesize them into a report.\n\n### Recommended Actions\n* Check the Analytics dashboard and Threat Matrix for numerical insights.\n* Review the raw signal stream in the Intelligence feed."
            return "[]"