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
    create_hypothesis_snapshot,
    save_analytics_snapshot
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

class HypothesisQualityValidator:
    def __init__(self):
        self.llm = get_groq_llm()

    def run_create_deterministic_gate(self, belief: str, prediction: str, company_name: str) -> dict:
        # Genericity check: Replacing company name
        generic_belief = re.sub(re.escape(company_name), "A company", belief, flags=re.IGNORECASE)
        # If removing the company name makes it a generic startup statement without any specific nouns
        # we do a simple heuristic: if the length of words is short and no other entities are present
        if len(generic_belief.split()) < 6:
            return {"pass": False, "reason": "GENERICITY_FAILURE: Belief is too brief and generic."}
        
        # Prediction check
        pred_words = prediction.split()
        if len(pred_words) < 5:
            return {"pass": False, "reason": "QUANTIFICATION_FAILURE: Statement is too vague."}
            
        def contains_future_claim(pred: str) -> bool:
            pred_lower = pred.lower()
            future_markers = ["will", "plans to", "expected to", "set to", "scheduled to", "going to", "soon"]
            if not any(marker in pred_lower for marker in future_markers):
                return False
                
            # Weak phrases that are NOT observable events
            weak_phrases = [
                "will grow", "continue growing", "will improve", "plans to improve", 
                "will expand capabilities", "will become", "will get better", 
                "competition will increase", "models will get better",
                "more partnerships soon", "more lawsuits will happen"
            ]
            if any(weak in pred_lower for weak in weak_phrases):
                return False
                
            # Must contain an observable action/event
            observable_actions = [
                "acquire", "launch", "introduce", "restrict", "announce", "spin off",
                "release", "sign", "delay", "open", "hire", "sunset", "implement", 
                "refuse", "drop", "open-source", "boast", "increase", "raise", "price"
            ]
            if not any(action in pred_lower for action in observable_actions):
                # If no specific observable action verb is found, fail it
                return False
                
            return True

        if not contains_future_claim(prediction):
            return {"pass": False, "reason": "TIME_HORIZON_FAILURE: No verifiable future claim or externally observable event."}

        return {"pass": True, "reason": "Passed deterministic gates."}

    def validate_create_action(self, action: dict, company_name: str) -> dict:
        belief = action.get("belief", "")
        prediction = action.get("prediction", "")
        tradeoff = action.get("strategic_tradeoff", "")

        # 1. Deterministic Checks First
        det_res = self.run_create_deterministic_gate(belief, prediction, company_name)
        if not det_res["pass"]:
            return {
                "pass": False,
                "genericity_score": 1,
                "ceo_score": 1,
                "falsifiability_score": 1,
                "reason": det_res["reason"]
            }

        # 2. LLM Quality Gate
        prompt = f"""
You are a strict strategic intelligence auditor.
Evaluate this new strategic hypothesis for {company_name}:

Belief: {belief}
Trade-off: {tradeoff}
Prediction: {prediction}

Score it strictly (1-5) on:
1. Genericity (1=generic topic, 5=highly specific to this company's unique situation)
2. Opposite Test (1=the opposite is equally plausible, 5=it stakes a bold specific claim)
3. CEO Test (1=obvious observation, 5=insight that could alter a CEO's decision)
4. Falsifiability (1=vague prediction, 5=highly specific, measurable prediction)

If ANY score is less than 3, the hypothesis FAILS (pass: false).

Return ONLY valid JSON:
{{
    "pass": true/false,
    "genericity_score": <int>,
    "opposite_score": <int>,
    "ceo_score": <int>,
    "falsifiability_score": <int>,
    "reason": "<Detailed explanation of why it passed or failed.>"
}}
"""
        try:
            resp = llm_invoke(self.llm, prompt)
            match = re.search(r"\{.*\}", resp, re.DOTALL)
            if match:
                res = json.loads(match.group())
                # Enforce fail if any score < 3
                if res.get("genericity_score", 0) < 3:
                    res["pass"] = False
                    res["reason"] = f"GENERICITY_FAILURE: {res.get('reason', '')}"
                elif res.get("ceo_score", 0) < 3:
                    res["pass"] = False
                    res["reason"] = f"CEO_TEST_FAILURE: {res.get('reason', '')}"
                elif res.get("falsifiability_score", 0) < 3:
                    res["pass"] = False
                    res["reason"] = f"QUANTIFICATION_FAILURE: {res.get('reason', '')}"
                elif res.get("opposite_score", 0) < 3:
                    res["pass"] = False
                    res["reason"] = f"GENERICITY_FAILURE: {res.get('reason', '')}"
                return res
        except Exception as e:
            logger.error(f"Validator LLM parse error: {e}")
            pass
        
        return {"pass": False, "genericity_score": 0, "opposite_score": 0, "ceo_score": 0, "falsifiability_score": 0, "reason": "Failed to parse validation."}

    def validate_update_action(self, existing_hyp: dict, action: dict, company_name: str) -> dict:
        prompt = f"""
You are a strict strategic intelligence auditor.
An existing hypothesis is being updated with new signals.

OLD BELIEF: {existing_hyp.get('title')}
NEW SIGNAL REASONING: {action.get('reasoning')}
CONFIDENCE ADJUSTMENT: {action.get('confidence_adjustment')}

Test for regression:
1. Specificity Regression (1=became generic mush, 5=maintained or increased specificity)
2. Prediction Regression (1=prediction became harder to falsify, 5=remains crisp)
3. Confidence Consistency (1=confidence increased but evidence is weak, 5=evidence strongly supports adjustment)

If ANY score is less than 3, the update FAILS (pass: false).

Return ONLY valid JSON:
{{
    "pass": true/false,
    "specificity_regression_score": <int>,
    "prediction_regression_score": <int>,
    "confidence_consistency_score": <int>,
    "reason": "<Detailed explanation.>"
}}
"""
        try:
            resp = llm_invoke(self.llm, prompt)
            match = re.search(r"\{.*\}", resp, re.DOTALL)
            if match:
                res = json.loads(match.group())
                if res.get("specificity_regression_score", 0) < 3 or res.get("prediction_regression_score", 0) < 3 or res.get("confidence_consistency_score", 0) < 3:
                    res["pass"] = False
                return res
        except Exception as e:
            logger.error(f"Validator LLM parse error: {e}")
            pass

        return {"pass": False, "specificity_regression_score": 0, "prediction_regression_score": 0, "confidence_consistency_score": 0, "reason": "Failed to parse validation."}

class HypothesisEngine:
    def __init__(self):
        self.llm = get_groq_llm()
        self.validator = HypothesisQualityValidator()
        self.metrics = {
            "hypotheses_created": 0,
            "hypotheses_deduplicated": 0,
            "evaluations_created": 0,
            "confidence_updates_applied": 0,
            "genericity_failures": 0,
            "ceo_test_failures": 0,
            "falsifiability_failures": 0,
            "update_regression_failures": 0,
            "quality_rejection_rate": 0.0,
            "average_quality_score": 0.0
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
            "confidence_updates_applied": 0,
            "genericity_failures": 0,
            "ceo_test_failures": 0,
            "falsifiability_failures": 0,
            "update_regression_failures": 0,
            "quality_rejection_rate": 0.0,
            "average_quality_score": 0.0
        }
        
        total_actions_evaluated = 0
        total_actions_rejected = 0
        quality_score_sum = 0

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
Your job is NOT to cluster topics. Your job is to extract underlying STRATEGIC TENSIONS from recent intelligence events for {company_name}.
The trigger for this generation is: {trigger_reason}

A valid hypothesis MUST explain:
1. What management is optimizing for.
2. What they are sacrificing (the trade-off).
3. What observable event should happen next if the belief is correct.

Recent Signals:
{context_str}

EXISTING HYPOTHESES for {company_name}:
{existing_hyps_str}

Based on the Recent Signals, what strategic tensions emerge? 
For EACH distinct tension you find:
1. Compare it to the EXISTING HYPOTHESES.
2. If the tension essentially describes the SAME strategic intent or risk as an existing hypothesis, output an "UPDATE" action.
3. If the tension is MATERIALLY DISTINCT and fundamentally new, output a "CREATE" action.

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
  "belief": "<A declarative strategic belief. E.g., 'Company is sacrificing margin to win enterprise distribution'>",
  "supporting_signals": ["<Short summary of supporting signal 1>", "<Short summary of supporting signal 2>"],
  "counter_evidence": ["<Any evidence that contradicts this belief, or 'None observed'>"],
  "strategic_tradeoff": "<What is being sacrificed for what gain?>",
  "prediction": "<What specific, observable event should happen next if this is true?>",
  "themes": [<List of themes exactly matching: {VALID_THEMES}>],
  "confidence": <float between 0.40 and 0.70>,
  "predicted_time_horizon": "90_days" // One of ["30_days", "90_days", "180_days", "365_days"]
}}

If the signals are just noise and no clear strategic tension emerges, return an empty array [].
Do NOT create duplicate hypotheses. Be strict about matching existing ones.

Output ONLY a valid JSON array.
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

                        total_actions_evaluated += 1
                        
                        # Validate regression
                        val_res = self.validator.validate_update_action(existing, action, company_name)
                        if not val_res.get("pass", False):
                            total_actions_rejected += 1
                            self.metrics["update_regression_failures"] += 1
                            save_analytics_snapshot("rejected_hypothesis_update", {
                                "action": action,
                                "existing_belief": existing.get("title"),
                                "scores": val_res,
                                "reason": val_res.get("reason", "")
                            })
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
                        total_actions_evaluated += 1
                        val_res = self.validator.validate_create_action(action, company_name)
                        
                        # Tally scores
                        g_score = val_res.get("genericity_score", 0)
                        c_score = val_res.get("ceo_score", 0)
                        f_score = val_res.get("falsifiability_score", 0)
                        o_score = val_res.get("opposite_score", 0)
                        quality_score_sum += (g_score + c_score + f_score + o_score) / 4.0

                        if not val_res.get("pass", False):
                            total_actions_rejected += 1
                            if g_score < 3: self.metrics["genericity_failures"] += 1
                            if c_score < 3: self.metrics["ceo_test_failures"] += 1
                            if f_score < 3: self.metrics["falsifiability_failures"] += 1
                            
                            save_analytics_snapshot("rejected_hypothesis_create", {
                                "action": action,
                                "scores": val_res,
                                "reason": val_res.get("reason", "")
                            })
                            continue

                        # Sanitize themes
                        themes = [t for t in action.get("themes", []) if t in VALID_THEMES]
                        
                        # Build formatted markdown description
                        support_list = "\n".join([f"- {s}" for s in action.get("supporting_signals", ["None"])])
                        counter_list = "\n".join([f"- {c}" for c in action.get("counter_evidence", ["None observed"])])
                        
                        desc_md = f"**Strategic Trade-off**:\n{action.get('strategic_tradeoff', 'None specified')}\n\n" \
                                  f"**Prediction**:\n{action.get('prediction', 'None specified')}\n\n" \
                                  f"**Counter-evidence**:\n{counter_list}\n\n" \
                                  f"**Supporting Evidence**:\n{support_list}"
                        
                        hyp_record = {
                            "company_id": company_id,
                            "type": action.get("type", "EXPANSION"),
                            "title": action.get("belief", "Unknown Strategic Belief"),
                            "description": desc_md,
                            "themes": themes,
                            "confidence": float(action.get("confidence", 0.50)),
                            "status": "ACTIVE",
                            "predicted_time_horizon": action.get("predicted_time_horizon", "90_days")
                        }
                        db_hyp = create_hypothesis(hyp_record)
                        if db_hyp:
                            created_or_updated.append(db_hyp)
                            self.metrics["hypotheses_created"] += 1

                if total_actions_evaluated > 0:
                    self.metrics["quality_rejection_rate"] = round(total_actions_rejected / total_actions_evaluated, 2)
                    self.metrics["average_quality_score"] = round(quality_score_sum / total_actions_evaluated, 2)

                logger.info(f"Engine produced {self.metrics['hypotheses_created']} creations and {self.metrics['hypotheses_deduplicated']} updates for {company_name}. Rejection rate: {self.metrics['quality_rejection_rate']}")
                return created_or_updated
            return []
        except Exception as e:
            logger.error(f"Error generating/updating hypotheses: {e}")
            return []
