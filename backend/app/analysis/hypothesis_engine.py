"""
Argos — Hypothesis Engine
Generates high-level strategic hypotheses based on correlations and recent signals.
"""

import logging
import json
import re
from app.llm import get_groq_llm, llm_invoke
from app.database import (
    create_hypothesis,
    get_active_and_confirmed_hypotheses,
    update_hypothesis,
    create_hypothesis_evaluation,
    create_hypothesis_snapshot
)

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
        self.metrics = {
            "hypotheses_created": 0,
            "hypotheses_deduplicated": 0,
            "evaluations_created": 0,
            "confidence_updates_applied": 0
        }

    def generate_hypotheses(self, company_id: str, company_name: str, recent_signals: list[dict], trigger_reason: str):
        """
        Takes recent signals, compares them to existing ACTIVE and CONFIRMED hypotheses,
        and either updates existing hypotheses (deduplication) or creates materially distinct new ones.
        """
        if not recent_signals:
            return []

        # Reset metrics for this run
        self.metrics = {
            "hypotheses_created": 0,
            "hypotheses_deduplicated": 0,
            "evaluations_created": 0,
            "confidence_updates_applied": 0
        }

        # 1. Fetch existing ACTIVE + CONFIRMED hypotheses
        existing_hyps = get_active_and_confirmed_hypotheses(company_id)
        existing_hyps_str = "None"
        if existing_hyps:
            existing_hyps_str = ""
            for h in existing_hyps:
                existing_hyps_str += f"- ID: {h['id']}\n  Title: {h['title']}\n  Description: {h['description']}\n  Confidence: {h['confidence']}\n\n"

        # Prepare context
        context_str = ""
        for s in recent_signals[:30]:
            context_str += f"- [{s.get('signal_type', 'UNKNOWN')}] {s.get('title', 'Event')}: {s.get('content', '')}\n"

        prompt = f"""
You are the Argos Intelligence Hypothesis Engine.
Your job is to look at recent intelligence events for {company_name} and generate high-level strategic hypotheses about what this company is currently attempting to do or what risks they are facing.
The trigger for this generation is: {trigger_reason}

Recent Signals:
{context_str}

EXISTING HYPOTHESES for {company_name}:
{existing_hyps_str}

Based on the Recent Signals, what strategic narratives emerge? 
For EACH distinct narrative you find:
1. Compare it to the EXISTING HYPOTHESES.
2. If the narrative essentially describes the SAME strategic intent or risk as an existing hypothesis (even if worded slightly differently), you MUST output an "UPDATE" action instead of creating a new one.
3. If the narrative is MATERIALLY DISTINCT and fundamentally new, output a "CREATE" action.

Return a JSON array of actions.

To update an existing hypothesis (DEDUPLICATION):
{{
  "action": "UPDATE",
  "hypothesis_id": "<exact ID of the existing hypothesis>",
  "confidence_adjustment": <float between -0.2 and 0.2 representing how these signals impact the hypothesis>,
  "reasoning": "<1-2 sentences explaining why the signals support or refute this existing hypothesis>"
}}

To create a NEW hypothesis:
{{
  "action": "CREATE",
  "type": "EXPANSION", // One of [EXPANSION, RISK, PRODUCT_PIVOT, ACQUISITION_TARGET, GEOGRAPHIC_EXPANSION, GO_TO_MARKET_EXPANSION]
  "title": "<A short, declarative title>",
  "description": "<A 1-2 sentence explanation>",
  "themes": [<List of themes exactly matching: {VALID_THEMES}>],
  "confidence": <float between 0.40 and 0.70>,
  "predicted_time_horizon": "90_days" // One of ["30_days", "90_days", "180_days", "365_days"]
}}

If the signals are just noise and no clear narrative emerges, return an empty array [].
Do NOT create duplicate hypotheses. Be strict about matching existing ones.

Output ONLY valid JSON array.
"""
        created_or_updated = []
        try:
            response = llm_invoke(self.llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                actions_data = json.loads(match.group())
                
                # Use the most recent signal ID for evaluations
                anchor_signal_id = recent_signals[0].get("id") if recent_signals else None

                for action in actions_data:
                    action_type = action.get("action", "").upper()
                    
                    if action_type == "UPDATE":
                        hyp_id = action.get("hypothesis_id")
                        if not hyp_id:
                            continue
                        
                        # Find the existing hyp object
                        existing = next((h for h in existing_hyps if str(h.get("id")) == str(hyp_id)), None)
                        if not existing:
                            continue

                        # Deduplication state tracking
                        self.metrics["hypotheses_deduplicated"] += 1

                        adjustment = float(action.get("confidence_adjustment", 0.0))
                        new_confidence = min(0.99, max(0.01, float(existing.get("confidence", 0.5)) + adjustment))
                        reasoning = action.get("reasoning", "Updated by HypothesisEngine.")

                        # Create evaluation
                        if anchor_signal_id:
                            create_hypothesis_evaluation({
                                "hypothesis_id": hyp_id,
                                "signal_id": anchor_signal_id,
                                "impact": adjustment,
                                "reasoning": reasoning
                            })
                            self.metrics["evaluations_created"] += 1

                        # Update confidence and create snapshot
                        if abs(adjustment) > 0.01:
                            update_hypothesis(hyp_id, {"confidence": new_confidence})
                            # update_hypothesis creates snapshot internally
                            self.metrics["confidence_updates_applied"] += 1
                        
                        created_or_updated.append(existing)
                        
                    elif action_type == "CREATE":
                        # Sanitize themes
                        themes = [t for t in action.get("themes", []) if t in VALID_THEMES]
                        
                        hyp_record = {
                            "company_id": company_id,
                            "type": action.get("type", "EXPANSION"),
                            "title": action.get("title", "Unknown Hypothesis"),
                            "description": action.get("description", ""),
                            "themes": themes,
                            "confidence": float(action.get("confidence", 0.50)),
                            "status": "ACTIVE",
                            "predicted_time_horizon": action.get("predicted_time_horizon", "90_days")
                        }
                        db_hyp = create_hypothesis(hyp_record)
                        if db_hyp:
                            created_or_updated.append(db_hyp)
                            self.metrics["hypotheses_created"] += 1

                logger.info(f"Engine produced {self.metrics['hypotheses_created']} creations and {self.metrics['hypotheses_deduplicated']} updates for {company_name}.")
                return created_or_updated
            return []
        except Exception as e:
            logger.error(f"Error generating/updating hypotheses: {e}")
            return []
