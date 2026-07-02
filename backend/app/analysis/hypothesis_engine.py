"""
Argos — Hypothesis Engine
Generates high-level strategic hypotheses based on correlations and recent signals.
"""

import logging
import json
import re
from app.llm import get_groq_llm, llm_invoke
from app.analysis.signal_compressor import compress_signals
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
        self._llm = None  # Lazy-loaded — constructor must not make network calls

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_groq_llm()
        return self._llm

<<<<<<< HEAD
    def run_create_deterministic_gate(self, interpretation: str, prediction: str, company_name: str) -> dict:
=======
    def run_create_deterministic_gate(self, belief: str, prediction_event: str, prediction_target: str, prediction_measurement: str, company_name: str, evidence_titles: list[str]) -> dict:
        # Reconstruct full prediction string for backward compatibility with existing checks
        prediction = f"{prediction_event} {prediction_target} {prediction_measurement}"
        
        # Concreteness Gate: reject fluffy narrative words
        fluff_words = [
            "major", "significant", "accelerate", "improve", "enhance", 
            "strengthen", "grow adoption", "increase adoption", 
            "expand presence", "drive growth", "support growth"
        ]
        pred_lower = prediction.lower()
        if any(fluff in pred_lower for fluff in fluff_words):
            return {"pass": False, "reason": "CONCRETENESS_FAILURE: Prediction relies on unmeasurable narrative fluff (e.g. 'major', 'accelerate') instead of concrete events."}
            
>>>>>>> a069832 (feat(analysis): implement structured prediction schema, concreteness gate, and add comprehensive audit scripts including CEO Test V3)
        # Genericity check: Replacing company name
        generic_interp = re.sub(re.escape(company_name), "A company", interpretation, flags=re.IGNORECASE)
        # If removing the company name makes it a generic startup statement without any specific nouns
        # we do a simple heuristic: if the length of words is short and no other entities are present
        if len(generic_interp.split()) < 6:
            return {"pass": False, "reason": "GENERICITY_FAILURE: Interpretation is too brief and generic."}
        
        # Prediction check
        if len(prediction_measurement.split()) < 4:
            return {"pass": False, "reason": "QUANTIFICATION_FAILURE: Prediction measurement is too vague."}

        # Freshness Gate: check if the prediction event has already occurred
        VERB_FAMILIES = {
            "announce": ["announce", "announced", "unveil", "unveiled"],
            "launch": ["launch", "launched", "release", "released"],
            "acquire": ["acquire", "acquired", "buy", "bought"],
            "partner": ["partner", "partnered", "alliance", "agreement"],
            "fund": ["fund", "funding", "raise", "raised"],
        }
        
        NOUN_FAMILIES = {
            "AI_CHIP": ["custom ai chip", "ai inference chip", "custom inference chip", "chip", "hardware"],
            "ENTERPRISE_DATA": ["enterprise data platform", "data loops", "proprietary data", "enterprise product"],
            "MODEL_RELEASE": ["model", "release", "api", "claude tag", "mythos", "fable"],
            "PARTNERSHIP": ["partnership", "agreement", "alliance", "deal"],
            "FUNDING": ["funding", "raise", "investment", "capital"]
        }
        
        pred_lower = prediction.lower()
        for v_family_name, v_synonyms in VERB_FAMILIES.items():
            if any(verb in pred_lower for verb in v_synonyms):
                # We found a verb. Now look for a noun family.
                for n_family_name, n_synonyms in NOUN_FAMILIES.items():
                    if any(noun in pred_lower for noun in n_synonyms):
                        # The prediction contains both a verb and a noun family.
                        # Now check if ANY evidence title contains BOTH.
                        for title in evidence_titles:
                            title_lower = title.lower()
                            if any(v in title_lower for v in v_synonyms) and any(n in title_lower for n in n_synonyms):
                                return {"pass": False, "reason": "FRESHNESS_FAILURE: Prediction already occurred in evidence.", "failed_gate": "freshness"}
        
        return {"pass": True, "reason": "Passed deterministic gates."}

<<<<<<< HEAD
    def validate_create_action(self, action: dict, company_name: str) -> dict:
        interpretation = action.get("interpretation") or action.get("belief", "")
        prediction = action.get("prediction", "")
        tradeoff = action.get("strategic_tradeoff", "")
        observation = action.get("observation", "")

        # 1. Deterministic Checks First
        det_res = self.run_create_deterministic_gate(interpretation, prediction, company_name)
=======
    def validate_create_action(self, action: dict, company_name: str, recent_signals: list[dict]) -> dict:
        belief = action.get("belief", "")
        prediction_event = action.get("prediction_event", "")
        prediction_target = action.get("prediction_target", "")
        prediction_measurement = action.get("prediction_measurement", "")
        prediction = f"{prediction_event} {prediction_target} {prediction_measurement}"
        tradeoff = action.get("strategic_tradeoff", "")
        evidence_titles = [s.get("title", "") for s in recent_signals]

        # 1. Deterministic Checks First
        det_res = self.run_create_deterministic_gate(belief, prediction_event, prediction_target, prediction_measurement, company_name, evidence_titles)
>>>>>>> a069832 (feat(analysis): implement structured prediction schema, concreteness gate, and add comprehensive audit scripts including CEO Test V3)
        if not det_res["pass"]:
            res = {
                "pass": False,
                "genericity_score": 1,
                "ceo_score": 1,
                "falsifiability_score": 1,
                "reason": det_res["reason"]
            }
            if det_res.get("failed_gate") == "freshness":
                res["failed_gate"] = "freshness"
            return res

        # 2. LLM Quality Gate
        prompt = f"""
You are a strict strategic intelligence auditor.
Evaluate this new strategic hypothesis for {company_name}:

Observation: {observation}
Interpretation: {interpretation}
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
        # 2000 tokens: enough for 5 tensions (with evidence) or 5 hypotheses
        # in a single response without mid-JSON truncation.
        # Validator keeps its own 500-token instance (single scored object).
        self.llm = get_groq_llm(max_tokens=2000)
        self.validator = HypothesisQualityValidator()
        self.metrics = {
            # ── Funnel (top → bottom) ──────────────────────────────────
            "signals_seen": 0,                 # raw signals passed in
            "signals_after_compression": 0,    # after compress_signals
            "tensions_extracted": 0,            # competing forces found (step 1)
            "tensions_overlap_checked": 0,      # how many valid pairs were overlap-checked
            "tensions_discarded_low_overlap": 0, # discarded due to no substantive shared concept
            "tensions_discarded_no_evidence": 0, # tensions dropped: < 2 signals per side
            "tension_examples": [],             # first 2 tension previews
            "candidate_actions_generated": 0,  # actions LLM proposed (pre-validation)
            "candidate_examples": [],            # first 3 raw previews (belief or reasoning)
            "validator_rejected": 0,           # CREATE actions killed by quality validator
            "dedup_rejected": 0,               # UPDATE actions killed by regression validator
            "final_created": 0,                # hypotheses written to DB
            "final_updated": 0,                # hypotheses confidence-updated in DB
            # ── Legacy / derived ──────────────────────────────────────
            "hypotheses_created": 0,
            "hypotheses_deduplicated": 0,
            "evaluations_created": 0,
            "confidence_updates_applied": 0,
            "genericity_failures": 0,
            "ceo_test_failures": 0,
            "falsifiability_failures": 0,
            "freshness_checked": 0,
            "freshness_rejected": 0,
            "update_regression_failures": 0,
            "quality_rejection_rate": 0.0,
            "average_quality_score": 0.0
        }

    def _extract_tensions(self, context_str: str, company_name: str) -> list[dict]:
        """
        Step 1 of 2-step generation (D.7B).

        Two key design decisions:

        1. BLIND EXTRACTION: The company name is hidden from the prompt (replaced
           with COMPANY_X). This tests whether the model was anchoring on its
           training knowledge of the company label rather than reading the signals.
           Signal content still contains the company name naturally.

        2. EVIDENCE GATEKEEPING: Tensions are discarded in Python if they cite
           fewer than 2 signals per side. No validator, no extra LLM call.
           Unsupported tensions simply don't pass.
        """
        # We employ an evidence-first strategy here:
        # Instead of allowing the model to invent tensions and then search for evidence,
        # we force the model to identify evidence first and then deduce the tension.
        prompt = f"""You are a strategic analyst. You have been given intelligence signals about COMPANY_X.

Your task is to identify COMPETING FORCES — pairs of signals that pull in opposite directions.

A tension exists when:
- One group of signals implies COMPANY_X is accelerating or committing to a direction
- A DIFFERENT group of signals implies constraint, resistance, or an opposing pressure
- Both directions cannot be fully optimized simultaneously

Do NOT invent a tension first and then search for evidence.
Work in this exact order:

STEP 1: Scan the signal list. Select 2-4 signal titles where COMPANY_X is clearly pursuing or accelerating something specific.
STEP 2: Scan the REMAINING signals. Select 2-4 DIFFERENT signal titles that show constraint, pushback, or a contradictory direction.
STEP 3: Only after selecting both groups, name the force each group represents.

Recent Signals:
{context_str}

Find up to 5 DISTINCT tension pairs. Each pair must draw from different signals.

Return ONLY valid JSON. Evidence fields come FIRST to reflect the reasoning order:
[
  {{
    "evidence_a": ["<Exact signal title 1>", "<Exact signal title 2>"],
    "evidence_b": ["<Exact signal title 3>", "<Exact signal title 4>"],
    "force_a": "<The direction COMPANY_X is pursuing, inferred from evidence_a only>",
    "force_b": "<The constraint or opposing pressure, inferred from evidence_b only>"
  }}
]

Rules:
- If you cannot find 2 real signal titles per side, skip that tension.
- Do not reuse the same signal title in multiple tensions.
- If no valid tensions exist, return [].
- Do not add any text outside the JSON array."""
        raw_tensions = []
        try:
            response = llm_invoke(self.llm, prompt)
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                if isinstance(parsed, list):
                    raw_tensions = parsed
        except Exception as e:
            logger.error(f"[{company_name}] Tension extraction failed: {e}")
            return []

        # Evidence gatekeeping: discard tensions with < 2 signals per side.
        # No LLM, no validator — pure Python filter.
        valid, discarded_evidence, discarded_overlap = [], 0, 0
        overlap_checked = 0
        
        for t in raw_tensions:
            ev_a = [s for s in t.get("evidence_a", []) if s.strip()]
            ev_b = [s for s in t.get("evidence_b", []) if s.strip()]
            if len(ev_a) >= 2 and len(ev_b) >= 2:
                overlap_checked += 1
                
                # LOW OVERLAP FILTER
                def get_clean_tokens(texts):
                    content = " ".join(texts).lower()
                    # Replace punctuation with space
                    content = re.sub(r'[^a-z0-9\s]', ' ', content)
                    tokens = set(content.split())
                    stop_words = {
                        "a", "an", "the", "and", "or", "but", "to", "for", "with", "on", "in", "of", 
                        "is", "are", "its", "it", "at", "by", "from", "as", "be", "this", "that", 
                        "which", "has", "have", "had", "will", "would", "could", "should", "s"
                    }
                    company_variations = {company_name.lower()}
                    return tokens - stop_words - company_variations
                
                meaningful_a = get_clean_tokens(ev_a)
                meaningful_b = get_clean_tokens(ev_b)
                
                shared = meaningful_a.intersection(meaningful_b)
                
                logger.debug(
                    f"[{company_name}] Overlap check:\n"
                    f"Force A: {t.get('force_a')}\n"
                    f"Force B: {t.get('force_b')}\n"
                    f"Overlap terms: {list(shared)}\n"
                    f"Decision: {'KEEP' if shared else 'DISCARD'}"
                )
                
                if not shared:
                    discarded_overlap += 1
                else:
                    valid.append(t)
            else:
                discarded_evidence += 1
                logger.debug(
                    f"[{company_name}] Discarded tension (insufficient evidence): "
                    f"A={t.get('force_a', '')[:60]} | ev_a={len(ev_a)} ev_b={len(ev_b)}"
                )

        self.metrics["tensions_discarded_no_evidence"] = discarded_evidence
        self.metrics["tensions_overlap_checked"] = overlap_checked
        self.metrics["tensions_discarded_low_overlap"] = discarded_overlap
        
        logger.info(
            f"[{company_name}] Tension extraction: {len(raw_tensions)} raw, "
            f"{discarded_evidence} discarded (no evidence), {discarded_overlap} discarded (low overlap), {len(valid)} valid."
        )
        return valid

    def generate_hypotheses(self, company_id: str, company_name: str, recent_signals: list[dict], trigger_reason: str):
        """
        Takes recent signals, compares them to existing ACTIVE and CONFIRMED hypotheses,
        and either updates existing hypotheses (deduplication) or creates materially distinct new ones.
        """
        if not recent_signals:
            return []

        # Reset metrics for this run
        self.metrics = {
            # ── Funnel (top → bottom) ──────────────────────────────────
            "signals_seen": 0,
            "signals_after_compression": 0,
            "tensions_extracted": 0,
            "tensions_overlap_checked": 0,
            "tensions_discarded_low_overlap": 0,
            "tensions_discarded_no_evidence": 0,
            "tension_examples": [],
            "candidate_actions_generated": 0,
            "candidate_examples": [],
            "validator_rejected": 0,
            "dedup_rejected": 0,
            "final_created": 0,
            "final_updated": 0,
            "proper_noun_count_avg": 0.0,
            # ── Legacy / derived ──────────────────────────────────────
            "update_missing_hypothesis_id": 0,
            "forced_create_conversions": 0,
            "hypotheses_created": 0,
            "hypotheses_deduplicated": 0,
            "evaluations_created": 0,
            "confidence_updates_applied": 0,
            "genericity_failures": 0,
            "ceo_test_failures": 0,
            "falsifiability_failures": 0,
            "freshness_checked": 0,
            "freshness_rejected": 0,
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

        # Track funnel entry points
        self.metrics["signals_seen"] = len(recent_signals)

        # Compress signals to observations — one centralized layer, deterministic
        compressed = compress_signals(recent_signals[:50])
        self.metrics["signals_after_compression"] = len(compressed)

        # Prepare context
        context_str = ""
        for s in compressed:
            context_str += f"- [{s.get('signal_type', 'UNKNOWN')}] {s.get('title', 'Event')}: {s.get('summary', '')}\n"

        # ── Step 1: Extract tensions ─────────────────────────────────────────
        # Force the model to name competing forces BEFORE generating any hypothesis.
        # If this returns [], we stop here — that's the diagnostic signal.
        tensions = self._extract_tensions(context_str, company_name)
        self.metrics["tensions_extracted"] = len(tensions)
        self.metrics["tension_examples"] = [
            {
                "force_a": t.get("force_a", "")[:150],
                "force_b": t.get("force_b", "")[:150],
                "evidence_a": t.get("evidence_a", [])[:2],
                "evidence_b": t.get("evidence_b", [])[:2],
            }
            for t in tensions[:2]
        ]

        if not tensions:
            logger.info(
                f"[{company_name}] Tension extraction returned 0 tensions. "
                f"Skipping hypothesis generation. "
                f"(signals_seen={self.metrics['signals_seen']}, "
                f"compressed={self.metrics['signals_after_compression']})"
            )
            return []

        # Build tension context for step 2
        tensions_str = ""
        for i, t in enumerate(tensions, 1):
            ev_a = "; ".join(t.get("evidence_a", []))
            ev_b = "; ".join(t.get("evidence_b", []))
            tensions_str += (
                f"\nTension {i}:\n"
                f"  Pursuing  (A): {t.get('force_a', '')}\n"
                f"  Competing (B): {t.get('force_b', '')}\n"
                f"  Evidence A: {ev_a}\n"
                f"  Evidence B: {ev_b}\n"
            )
        # ─────────────────────────────────────────────────────────────────────

        prompt = f"""
You are the Argos Intelligence Hypothesis Engine.
The trigger for this generation is: {trigger_reason}

A strategic analyst has already identified the following COMPETING FORCES for {company_name}:
{tensions_str}

EXISTING HYPOTHESES for {company_name}:
{existing_hyps_str}

{"CRITICAL: There are NO existing hypotheses. You MUST use CREATE actions ONLY. UPDATE actions are explicitly forbidden." if not existing_hyps else "For EACH tension above, determine:\n1. Does this tension map onto an EXISTING hypothesis (same strategic intent)? → output an UPDATE action.\n2. Is this tension a genuinely NEW belief not yet captured? → output a CREATE action."}

═══════════════════════════════════════════════════
CREATE SCHEMA — MANDATORY QUALITY RULES
═══════════════════════════════════════════════════

For every CREATE action you MUST produce the following fields in sequence:

1. OBSERVATION
   - State only facts directly supported by the evidence above.
   - Must reference at least 2 specific items from the evidence (names, products, events, deals).
   - ZERO strategic language. No "suggests", "prioritizes", "bets". Only what was observed.
   - Example: "{company_name} signed data-sharing agreements with LiveRamp and Getty Images while
     simultaneously disclosing that Codex is causing destructive SSD write amplification on user devices."

2. INTERPRETATION / STRATEGIC BET
   - Explain WHY the observation matters strategically. What is management BETTING ON (force_a prevailing) and SACRIFICING (force_b deprioritized).
   - MUST contain at least 2 proper nouns from the evidence (product names, partner names, people).
   - MUST be impossible to apply unchanged to any other company — if you can swap {company_name}
     for "Anthropic" and still make sense, REJECT and rewrite.
   - Example: "{company_name}'s LiveRamp and Getty partnerships suggest it is building proprietary
     enterprise data loops to differentiate from pure model-capability competitors like Anthropic."

3. STRUCTURED PREDICTION
   - You MUST structure the prediction into event, target, deadline (days), and measurement.
   - Predict one SPECIFIC, OBSERVABLE EVENT that would confirm the bet within 30-365 days.
   - Do NOT use fluffy words like "major", "accelerate", or "improve".
   - Structured fields:
     * prediction_event: specific action (e.g. launch, delay, acquire, sign, open-source)
     * prediction_target: the specific product, entity, or metric (e.g. 'Claude Tag')
     * prediction_deadline_days: an integer number of days (e.g. 90 or 180)
     * prediction_measurement: highly specific observable condition that proves the bet.

═══════════════════════════════════════════════════
SELF-CHECK (run before returning each hypothesis)
═══════════════════════════════════════════════════

Before returning, verify:
  A. Can I swap {company_name} with another tech company and have the interpretation still make sense?
     If YES → rewrite until it's hyper-specific.
  B. Does the prediction describe a specific observable event (acquire, launch, announce, sign, delay) and measurement?
     If NO → rewrite the prediction fields.
  C. Does the interpretation contain at least 2 proper nouns from the evidence?
     If NO → rewrite the interpretation.

Return a JSON array of actions.

To update an existing hypothesis (DEDUPLICATION):
{{
  "action": "UPDATE",
  "hypothesis_id": "<exact ID of the existing hypothesis>",
  "confidence_adjustment": <float between -0.2 and 0.2>,
  "reasoning": "<1-2 sentences on why this tension supports or refutes the existing hypothesis>"
}}

To create a NEW hypothesis:
{{
  "action": "CREATE",
  "type": "EXPANSION",
  "observation": "<Factual observation referencing ≥2 evidence items by name>",
  "interpretation": "<Strategic insight containing ≥2 proper nouns. Must be hyper-specific to {company_name}.>",
  "supporting_signals": ["<Evidence A>", "<Evidence B>"],
  "counter_evidence": ["<Evidence B, or None observed>"],
  "strategic_tradeoff": "<force_a gain with proper nouns> at the cost of <force_b loss>",
  "prediction_event": "<e.g., launch, delay, acquire, sign, open-source>",
  "prediction_target": "<The specific product, entity, or metric, e.g. 'Claude Tag'>",
  "prediction_deadline_days": <int, e.g. 90 or 180>,
  "prediction_measurement": "<Highly specific, observable condition that proves the bet, e.g. 'deployment postponed beyond announced roadmap'>",
  "themes": [<Themes from: {VALID_THEMES}>],
  "confidence": <float 0.40–0.70>,
  "predicted_time_horizon": "90_days"
}}

Output ONLY a valid JSON array. Do NOT create duplicate hypotheses.
"""
        created_or_updated = []
        try:
            response = llm_invoke(self.llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                actions_data = json.loads(match.group())

                # Record candidate count + first 3 examples BEFORE any validation
                self.metrics["candidate_actions_generated"] = len(actions_data)
                
                # Count average proper nouns (capitalised words, excluding sentence starts)
                # as a proxy for specificity
                def _count_proper_nouns(text: str) -> int:
                    words = text.split()
                    return sum(
                        1 for i, w in enumerate(words)
                        if w and w[0].isupper() and (i == 0 or not words[i-1].endswith("."))
                        and len(w) > 1
                    )
                
                create_candidates = [a for a in actions_data if a.get("action", "").upper() == "CREATE"]
                if create_candidates:
                    total_pn = sum(
                        _count_proper_nouns(a.get("interpretation", a.get("belief", "")))
                        for a in create_candidates
                    )
                    self.metrics["proper_noun_count_avg"] = round(total_pn / len(create_candidates), 1)
                
                self.metrics["candidate_examples"] = [
                    {
                        "action": a.get("action", "?"),
                        "preview": (
                            a.get("interpretation", a.get("belief", a.get("reasoning", "")))[:200]
                        )
                    }
                    for a in actions_data[:3]
                ]

                # ── Early-exit guard ────────────────────────────────────────
                # If the LLM returned an empty array, we early exit here
                # to prevent unnecessary processing, validation, and DB calls.
                if not actions_data:
                    logger.info(f"HypothesisEngine: LLM returned empty actions for {company_name}.")
                    return []
                # ────────────────────────────────────────────────────────────

                # Use the most recent signal ID for evaluations
                anchor_signal_id = recent_signals[0].get("id") if recent_signals else None

                for action in actions_data:
                    action_type = action.get("action", "").upper()
                    
                    if action_type == "UPDATE" and not existing_hyps:
                        self.metrics["forced_create_conversions"] += 1
                        action_type = "CREATE"
                        logger.warning(f"Forced CREATE conversion for {company_name}: LLM emitted UPDATE despite no existing hypotheses.")
                    
                    if action_type == "UPDATE":
                        hyp_id = action.get("hypothesis_id")
                        if not hyp_id:
                            self.metrics["update_missing_hypothesis_id"] += 1
                            continue
                        
                        # Find the existing hyp object
                        existing = next((h for h in existing_hyps if str(h.get("id")) == str(hyp_id)), None)
                        if not existing:
                            self.metrics["update_missing_hypothesis_id"] += 1
                            logger.warning(f"Dropped UPDATE candidate for {company_name}: Fake or missing hypothesis_id '{hyp_id}'")
                            continue

                        total_actions_evaluated += 1
                        
                        # Validate regression
                        val_res = self.validator.validate_update_action(existing, action, company_name)
                        if not val_res.get("pass", False):
                            total_actions_rejected += 1
                            self.metrics["update_regression_failures"] += 1
                            self.metrics["dedup_rejected"] += 1
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
                            self.metrics["final_updated"] += 1
                        
                        created_or_updated.append(existing)
                        
                    elif action_type == "CREATE":
                        total_actions_evaluated += 1
                        self.metrics["freshness_checked"] += 1
                        val_res = self.validator.validate_create_action(action, company_name, recent_signals)
                        
                        # Tally scores
                        g_score = val_res.get("genericity_score", 0)
                        c_score = val_res.get("ceo_score", 0)
                        f_score = val_res.get("falsifiability_score", 0)
                        o_score = val_res.get("opposite_score", 0)
                        quality_score_sum += (g_score + c_score + f_score + o_score) / 4.0

                        if not val_res.get("pass", False):
                            total_actions_rejected += 1
                            self.metrics["validator_rejected"] += 1
                            if g_score < 3: self.metrics["genericity_failures"] += 1
                            if c_score < 3: self.metrics["ceo_test_failures"] += 1
                            if f_score < 3: self.metrics["falsifiability_failures"] += 1
                            if val_res.get("failed_gate") == "freshness":
                                self.metrics["freshness_rejected"] += 1
                            
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
                        observation_text = action.get("observation", "")
                        
                        pred_event = action.get("prediction_event", "")
                        pred_target = action.get("prediction_target", "")
                        pred_days = action.get("prediction_deadline_days", "N/A")
                        pred_measure = action.get("prediction_measurement", "")
                        formatted_prediction = f"Event: {pred_event}\nTarget: {pred_target}\nDeadline: {pred_days} days\nMeasurement: {pred_measure}"
                        
                        desc_md = (f"**Observation**:\n{observation_text}\n\n" if observation_text else "") + \
                                  f"**Strategic Trade-off**:\n{action.get('strategic_tradeoff', 'None specified')}\n\n" \
                                  f"**Prediction**:\n{formatted_prediction}\n\n"
                                  f"**Counter-evidence**:\n{counter_list}\n\n" \
                                  f"**Supporting Evidence**:\n{support_list}"
                        
                        hyp_record = {
                            "company_id": company_id,
                            "type": action.get("type", "EXPANSION"),
                            # Use interpretation as the title; fall back to legacy belief field
                            "title": action.get("interpretation") or action.get("belief", "Unknown Strategic Belief"),
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
                            self.metrics["final_created"] += 1

                if total_actions_evaluated > 0:
                    self.metrics["quality_rejection_rate"] = round(total_actions_rejected / total_actions_evaluated, 2)
                    self.metrics["average_quality_score"] = round(quality_score_sum / total_actions_evaluated, 2)

                logger.info(
                    f"[{company_name}] Funnel: "
                    f"signals={self.metrics['signals_seen']} → "
                    f"compressed={self.metrics['signals_after_compression']} → "
                    f"candidates={self.metrics['candidate_actions_generated']} → "
                    f"validator_rejected={self.metrics['validator_rejected']} | "
                    f"dedup_rejected={self.metrics['dedup_rejected']} → "
                    f"final_created={self.metrics['final_created']} | "
                    f"final_updated={self.metrics['final_updated']}"
                )
                return created_or_updated
            return []
        except Exception as e:
            logger.error(f"Error generating/updating hypotheses: {e}")
            return []
