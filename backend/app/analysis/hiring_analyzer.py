import json
import logging
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

class HiringAnalyzer:
    def analyze_hiring_intent(
        self, 
        company_name: str,
        job_signals: list[dict]
    ) -> dict:
        """
        Analyze job postings to infer strategic intent.
        Returns {intent, evidence, confidence, roles_by_category}
        """
        if not job_signals:
            return {
                "intent": "Insufficient data",
                "evidence": [],
                "confidence": 0,
                "roles_by_category": {}
            }
        
        job_titles = [s.get("title", "") for s in job_signals]
        
        llm = get_groq_llm()
        prompt = f"""
You are a strategic analyst specializing in reading hiring signals.

Company: {company_name}
Recent job postings:
{chr(10).join(f"- {title}" for title in job_titles[:30])}

Analyze these job postings and return ONLY valid JSON:
{{
  "intent": "One sentence describing what this company is building or prioritizing based on hiring",
  "evidence": ["evidence point 1", "evidence point 2", "evidence point 3"],
  "confidence": 85,
  "roles_by_category": {{
    "Engineering": 12,
    "AI/ML": 8,
    "Product": 4,
    "Sales": 3,
    "Design": 2
  }},
  "key_signal": "The most important hiring signal in one sentence"
}}
"""
        try:
            response = llm_invoke(llm, prompt)
            text = response.content if hasattr(response, 'content') \
                else str(response)
            text = text.strip().replace('```json','').replace('```','').strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Hiring analysis failed: {e}")
            return {
                "intent": "Analysis failed",
                "evidence": [],
                "confidence": 0,
                "roles_by_category": {}
            }