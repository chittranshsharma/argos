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
    def extract_executive_movements(
        self,
        company_name: str,
        signals: list[dict]
    ) -> list[dict]:
        """
        Scan news and LinkedIn signals for executive movements.
        Returns list of {name, title, movement_type, source_url}
        """
        movements = []
        
        # Filter relevant signals
        relevant = [
            s for s in signals
            if s.get("source") in ["news", "linkedin"]
            and any(
                title in (s.get("title", "") + s.get("content", "")).lower()
                for title in EXECUTIVE_TITLES
            )
        ]
        
        if not relevant:
            return []
        
        llm = get_groq_llm()
        combined_text = "\n".join([
            f"- {s.get('title', '')}: {(s.get('content') or '')[:200]}"
            for s in relevant[:10]
        ])
        
        prompt = f"""
You are analyzing news about {company_name} for executive movements.

Signals:
{combined_text}

Extract any executive joins/departures/promotions.
Return ONLY valid JSON array (empty array if none found):
[
  {{
    "name": "Person Name",
    "title": "Their Title",
    "movement_type": "joined" or "left" or "promoted",
    "summary": "One sentence description"
  }}
]
"""
        try:
            response = llm_invoke(llm, prompt)
            text = response.content if hasattr(response, 'content') \
                else str(response)
            text = text.strip().replace('```json','').replace('```','').strip()
            movements = json.loads(text)
            return movements if isinstance(movements, list) else []
        except Exception as e:
            logger.error(f"Executive tracking failed: {e}")
            return []