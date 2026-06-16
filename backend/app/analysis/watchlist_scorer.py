"""
Argos — Watchlist Scorer
Deterministically scores incoming signals against active hypotheses.
No LLM used. Pure rules engine.
"""

import logging
from datetime import datetime, timezone
from app.database import get_active_hypotheses, update_hypothesis, create_hypothesis_evaluation, save_alert
from app.signals.registry import SignalSubtype

logger = logging.getLogger(__name__)

# Map signal subtypes to specific themes
SUBTYPE_TO_THEME_IMPACT = {
    # Positive confirmers
    SignalSubtype.AI_EXPANSION.value: {"themes": ["AI_INFRASTRUCTURE", "GPU", "TRAINING", "ML_PLATFORM"], "impact": 0.10, "desc": "AI Hiring confirms AI infrastructure focus."},
    SignalSubtype.GTM_PUSH.value: {"themes": ["GTM", "SALES", "MARKETING", "GO_TO_MARKET_EXPANSION"], "impact": 0.10, "desc": "GTM hiring confirms go-to-market expansion."},
    SignalSubtype.ENGINEERING_SURGE.value: {"themes": ["AI_INFRASTRUCTURE", "TRAINING"], "impact": 0.05, "desc": "General engineering surge weakly supports infrastructure growth."},
    SignalSubtype.CEO_APPOINTED.value: {"themes": ["LEADERSHIP", "EXECUTIVE_TEAM"], "impact": 0.15, "desc": "Major leadership appointment."},
    SignalSubtype.CEO_DEPARTED.value: {"themes": ["LEADERSHIP", "EXECUTIVE_TEAM"], "impact": 0.15, "desc": "Major leadership departure."},
    SignalSubtype.SERIES_A.value: {"themes": ["FUNDING", "CAPITAL_EXPANSION"], "impact": 0.15, "desc": "Significant capital injection."},
    SignalSubtype.SERIES_B.value: {"themes": ["FUNDING", "CAPITAL_EXPANSION"], "impact": 0.15, "desc": "Significant capital injection."},
    SignalSubtype.SERIES_C.value: {"themes": ["FUNDING", "CAPITAL_EXPANSION"], "impact": 0.15, "desc": "Significant capital injection."},
    SignalSubtype.ACQUISITION.value: {"themes": ["M_AND_A", "ACQUISITION"], "impact": 0.20, "desc": "Acquisition executed."},
    SignalSubtype.OPEN_SOURCE_EXPANSION.value: {"themes": ["OPEN_SOURCE", "DEVELOPER_COMMUNITY"], "impact": 0.10, "desc": "GitHub velocity confirms open source momentum."},
    
    # Negative impactors (Rejectors)
    SignalSubtype.HIRING_FREEZE.value: {"themes": ["EXPANSION", "AI_INFRASTRUCTURE", "GTM"], "impact": -0.15, "desc": "Hiring freeze contradicts expansion hypotheses."},
    SignalSubtype.MAINTENANCE_DECLINE.value: {"themes": ["OPEN_SOURCE", "DEVELOPER_COMMUNITY"], "impact": -0.10, "desc": "Engineering decline contradicts open source momentum."}
}

class WatchlistScorer:
    def __init__(self):
        self.CONFIRM_THRESHOLD = 0.85
        self.REJECT_THRESHOLD = 0.30

    def evaluate_signal(self, company_id: str, signal: dict):
        """
        Takes a new signal and evaluates it against all active hypotheses for the company.
        """
        active_hypotheses = get_active_hypotheses(company_id)
        if not active_hypotheses:
            return

        subtype = signal.get("subtype")
        if not subtype:
            return

        rule = SUBTYPE_TO_THEME_IMPACT.get(subtype)
        if not rule:
            return

        signal_id = signal.get("id")

        for hyp in active_hypotheses:
            hyp_themes = hyp.get("themes", [])
            
            # Check for theme intersection
            intersection = set(rule["themes"]).intersection(set(hyp_themes))
            if intersection:
                current_conf = float(hyp.get("confidence", 0.50))
                new_conf = round(current_conf + rule["impact"], 2)
                
                # Cap at 1.0 and 0.0
                new_conf = max(0.0, min(1.0, new_conf))
                
                status = hyp.get("status")
                if new_conf >= self.CONFIRM_THRESHOLD:
                    status = "CONFIRMED"
                elif new_conf <= self.REJECT_THRESHOLD:
                    status = "REJECTED"
                
                # Update hypothesis (this will also create a snapshot via DB hook)
                update_hypothesis(hyp["id"], {
                    "confidence": new_conf,
                    "status": status
                })
                
                # Check for Contradiction (Impact <= -0.15 AND Old Confidence >= 0.75)
                if rule["impact"] <= -0.15 and current_conf >= 0.75:
                    save_alert({
                        "company_id": company_id,
                        "company_name": signal.get("company_name", "Unknown"),
                        "alert_type": "CONTRADICTION DETECTED",
                        "message": f"🚨 Contradiction: Strong belief '{hyp.get('title')}' contradicted by new signal '{signal.get('title')}'.",
                        "sent_via": [],
                        "is_sent": False,
                        "confidence_score": current_conf,
                        "impact_level": "Critical"
                    })
                
                # Create evaluation record
                eval_record = {
                    "hypothesis_id": hyp["id"],
                    "signal_id": signal_id,
                    "impact": rule["impact"],
                    "reasoning": f"Deterministic Match: Signal subtype '{subtype}' maps to hypothesis themes {list(intersection)}. {rule['desc']}"
                }
                create_hypothesis_evaluation(eval_record)
                
                logger.info(f"WatchlistScorer updated Hypothesis {hyp['id']} to {new_conf} ({status}) based on {subtype}.")
