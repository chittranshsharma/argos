"""
Argos — Hypothesis Engine
Generates high-level strategic hypotheses based on correlations and recent signals.
"""

import logging
import json
import re
from app.llm import get_groq_llm, llm_invoke
from app.database import create_hypothesis

logger = logging.getLogger(__name__)

# Valid theme constants mapped to signal subtypes for the deterministic scorer later
VALID_THEMES = [
    "AI_INFRASTRUCTURE", "GPU", "TRAINING", "ML_PLATFORM",
    "GTM", "SALES", "MARKETING",
    "LEADERSHIP", "EXECUTIVE_TEAM",
    "OPEN_SOURCE", "DEVELOPER_COMMUNITY",
    "FUNDING", "CAPITAL_EXPANSION",
    "LAYOFFS", "COST_CUTTING", "RESTRUCTURING",
    "M_AND_A", "ACQUISITION"
]

class HypothesisEngine:
    def __init__(self):
        self.llm = get_groq_llm()

    def generate_hypotheses(self, company_id: str, company_name: str, recent_signals: list[dict], trigger_reason: str):
        """
        Takes recent signals (including correlations) and generates new hypotheses.
        """
        if not recent_signals:
            return []

        # Prepare context
        context_str = ""
        for s in recent_signals[:30]: # Cap at 30 recent signals to avoid context window blowouts
            context_str += f"- [{s.get('signal_type', 'UNKNOWN')}] {s.get('title', 'Event')}: {s.get('content', '')}\n"

        prompt = f"""
You are the Argos Intelligence Hypothesis Engine.
Your job is to look at recent intelligence events for {company_name} and generate 1-3 high-level strategic hypotheses about what this company is currently attempting to do or what risks they are facing.
The trigger for this generation is: {trigger_reason}

Recent Signals:
{context_str}

Return a JSON array of hypotheses. Each hypothesis must have:
- "type": One of [EXPANSION, RISK, PRODUCT_PIVOT, ACQUISITION_TARGET, GEOGRAPHIC_EXPANSION, GO_TO_MARKET_EXPANSION]
- "title": A short, declarative title (e.g., "Expanding model training infrastructure")
- "description": A 1-2 sentence explanation.
- "themes": A list of themes exactly matching the allowed list: {VALID_THEMES}
- "confidence": A float between 0.40 and 0.70 (since these are just initial guesses).

If the signals are just noise and no clear narrative is emerging, return an empty array [].

Only output valid JSON.
Example:
[
  {{
    "type": "EXPANSION",
    "title": "Scaling AI Training Infrastructure",
    "description": "The company has raised capital and immediately surged hiring for GPU and distributed systems engineers.",
    "themes": ["AI_INFRASTRUCTURE", "GPU", "TRAINING", "CAPITAL_EXPANSION"],
    "confidence": 0.65
  }}
]
"""
        try:
            response = llm_invoke(self.llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                hypotheses_data = json.loads(match.group())
                
                created = []
                for h in hypotheses_data:
                    # Sanitize themes
                    themes = [t for t in h.get("themes", []) if t in VALID_THEMES]
                    
                    hyp_record = {
                        "company_id": company_id,
                        "type": h.get("type", "EXPANSION"),
                        "title": h.get("title", "Unknown Hypothesis"),
                        "description": h.get("description", ""),
                        "themes": themes,
                        "confidence": float(h.get("confidence", 0.50)),
                        "status": "ACTIVE"
                    }
                    db_hyp = create_hypothesis(hyp_record)
                    if db_hyp:
                        created.append(db_hyp)
                
                logger.info(f"Generated {len(created)} hypotheses for {company_name}.")
                return created
            return []
        except Exception as e:
            logger.error(f"Error generating hypotheses: {e}")
            return []
