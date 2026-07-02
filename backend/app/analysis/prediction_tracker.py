"""
Argos — Prediction Outcome Tracker (Sprint 5A)

Runs autonomously in the background to evaluate active predictions against
incoming signals and transition them through the Forecast Registry state machine.

State machine (CONTRADICTED is NOT terminal — recovery allowed):

    UNRESOLVED ──→ SUPPORTED ──→ CONFIRMED  (terminal)
    UNRESOLVED ──→ CONTRADICTED ──→ CONFIRMED  (recovery)
                         └────────→ INCORRECT  (terminal)
    UNRESOLVED | SUPPORTED | CONTRADICTED ──→ EXPIRED  (terminal, deterministic)

No calibration logic here. That is Sprint 5C, after 50+ resolved predictions.
"""

import logging
import json
import re
from datetime import datetime, timezone, timedelta

from app.llm import get_groq_llm, llm_invoke
from app.database import (
    get_pending_prediction_outcomes,
    update_prediction_outcome,
    get_signals,
    update_hypothesis,
    PREDICTION_TERMINAL_STATES,
)

logger = logging.getLogger(__name__)

# Verdicts that advance the state machine vs those that hold
_ADVANCE_VERDICTS = {"SUPPORTED", "CONTRADICTED", "CONFIRMED"}

# Mapping LLM verdict → new prediction_outcome status
# CONTRADICTED is NOT terminal; the hypothesis status stays ACTIVE.
# Only CONFIRMED or INCORRECT are terminal for the hypothesis itself.
_VERDICT_TO_STATUS = {
    "SUPPORTED":    "SUPPORTED",
    "CONTRADICTED": "CONTRADICTED",
    "CONFIRMED":    "CONFIRMED",
    "UNCHANGED":    None,  # no-op
}

# If outcome reaches CONFIRMED → hypothesis outcome = CORRECT
# If outcome reaches INCORRECT (from CONTRADICTED) → hypothesis outcome = INCORRECT
_OUTCOME_MAP = {
    "CONFIRMED": "CORRECT",
    "INCORRECT":  "INCORRECT",
}


class PredictionTracker:
    """
    Evaluates all non-terminal predictions once per scheduler cycle.
    Phase 1: Deterministic deadline enforcement (no LLM).
    Phase 2: LLM evidence classification.
    """

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_groq_llm(max_tokens=400)
        return self._llm

    # ─────────────────────────────────────────────────────────────────────────
    # Entry point
    # ─────────────────────────────────────────────────────────────────────────

    def run(self) -> dict:
        """
        Main cycle. Returns summary metrics for the scheduler log.
        """
        pending = get_pending_prediction_outcomes()
        logger.info(f"[PredictionTracker] {len(pending)} pending outcomes to evaluate.")

        expired = 0
        advanced = 0
        unchanged = 0
        errors = 0

        for outcome in pending:
            try:
                hyp = outcome.get("hypotheses", {})
                if not hyp:
                    continue

                outcome_id    = outcome["id"]
                current_status = outcome["status"]
                company_id    = hyp.get("company_id", "")
                company_name  = hyp.get("title", "Unknown")[:40]

                # ── Phase 1: Hard Deadline ───────────────────────────────
                if self._is_expired(hyp, outcome):
                    update_prediction_outcome(
                        outcome_id=outcome_id,
                        status="EXPIRED",
                        reason="Prediction deadline passed without confirmation.",
                        evidence_signal_ids=outcome.get("evidence_signal_ids", []),
                        evidence_count=outcome.get("evidence_count", 0),
                        verdict_payload={"auto": "deadline_expired"},
                        confidence=0.0,
                    )
                    # Mark hypothesis as resolved/expired
                    update_hypothesis(hyp["id"], {
                        "status": "EXPIRED",
                        "outcome": "INCORRECT",
                        "resolution_reason": "Prediction deadline passed without confirmation.",
                        "resolved_at": datetime.now(timezone.utc).isoformat(),
                    })
                    expired += 1
                    logger.info(f"[PredictionTracker] EXPIRED: {hyp.get('id')} ({company_name})")
                    continue

                # ── Phase 2: LLM Evidence Classification ─────────────────
                signals = get_signals(company_id, limit=30)
                if not signals:
                    unchanged += 1
                    continue

                verdict = self._classify_evidence(hyp, signals)
                new_status = _VERDICT_TO_STATUS.get(verdict["verdict"])

                if new_status is None:
                    # UNCHANGED — no state change
                    unchanged += 1
                    continue

                # Determine whether this resolves the hypothesis
                is_terminal = (
                    new_status == "CONFIRMED" or
                    (new_status == "CONFIRMED" and current_status == "CONTRADICTED") or
                    (current_status == "CONTRADICTED" and new_status == "CONTRADICTED")
                )

                # CONTRADICTED → CONFIRMED: recovery case → mark CONFIRMED terminal
                # CONTRADICTED + another CONTRADICTED verdict → mark INCORRECT terminal
                final_status = new_status
                if current_status == "CONTRADICTED" and new_status == "CONTRADICTED":
                    # Second consecutive contradiction: transition to terminal INCORRECT
                    final_status = "INCORRECT"
                    logger.info(f"[PredictionTracker] INCORRECT (double contradiction): {hyp.get('id')}")
                elif current_status == "CONTRADICTED" and new_status == "CONFIRMED":
                    # Recovery! Override to CONFIRMED
                    final_status = "CONFIRMED"
                    logger.info(f"[PredictionTracker] CONFIRMED (recovered from contradiction): {hyp.get('id')}")

                matching_ids = [s["id"] for s in signals if s.get("title") in verdict.get("matching_signals", [])]
                all_ids = list(set(outcome.get("evidence_signal_ids", []) + matching_ids))

                update_prediction_outcome(
                    outcome_id=outcome_id,
                    status=final_status,
                    reason=verdict.get("reasoning", ""),
                    evidence_signal_ids=all_ids,
                    evidence_count=len(all_ids),
                    verdict_payload=verdict,
                    confidence=verdict.get("confidence", 0.5),
                )

                # Sync hypothesis if terminal
                if final_status in PREDICTION_TERMINAL_STATES:
                    hyp_outcome = _OUTCOME_MAP.get(final_status)
                    if hyp_outcome:
                        update_hypothesis(hyp["id"], {
                            "status": "RESOLVED",
                            "outcome": hyp_outcome,
                            "resolution_reason": verdict.get("reasoning", ""),
                            "resolved_at": datetime.now(timezone.utc).isoformat(),
                        })

                advanced += 1
                logger.info(
                    f"[PredictionTracker] {current_status} → {final_status} "
                    f"for {hyp.get('id')} ({company_name})"
                )

            except Exception as e:
                logger.error(f"[PredictionTracker] Error processing outcome {outcome.get('id')}: {e}")
                errors += 1

        summary = {
            "total_evaluated": len(pending),
            "expired": expired,
            "advanced": advanced,
            "unchanged": unchanged,
            "errors": errors,
        }
        logger.info(f"[PredictionTracker] Cycle complete: {summary}")
        return summary

    # ─────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _is_expired(self, hyp: dict, outcome: dict) -> bool:
        """Pure Python: check if prediction_deadline_days has elapsed."""
        deadline_days = hyp.get("prediction_deadline_days")
        if not deadline_days:
            return False
        try:
            created_str = hyp.get("created_at", "")
            if not created_str:
                return False
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            deadline = created_at + timedelta(days=int(deadline_days))
            return datetime.now(timezone.utc) > deadline
        except Exception:
            return False

    def _classify_evidence(self, hyp: dict, signals: list[dict]) -> dict:
        """
        Ask Llama-3-70b whether recent signals SUPPORT, CONTRADICT, CONFIRM, or are UNCHANGED
        relative to this hypothesis' structured prediction.
        """
        pred_event   = hyp.get("prediction_event", "")
        pred_target  = hyp.get("prediction_target", "")
        pred_measure = hyp.get("prediction_measurement", "")
        pred_days    = hyp.get("prediction_deadline_days", "N/A")

        # Compact signal context — most recent 20, title + summary only
        signal_lines = "\n".join([
            f"- [{s.get('signal_type', '?')}] {s.get('title', '')}: {str(s.get('summary', s.get('content', '')))[:120]}"
            for s in signals[:20]
        ])

        prompt = f"""You are Argos Prediction Auditor. Your job is to review recent signals and evaluate whether they support, contradict, confirm, or have no bearing on a specific strategic prediction.

PREDICTION:
- Event:       {pred_event}
- Target:      {pred_target}
- Deadline:    {pred_days} days from hypothesis creation
- Measurement: {pred_measure}

RECENT SIGNALS (most recent first):
{signal_lines}

Classify the weight of evidence using EXACTLY one of:
- CONFIRMED: A specific signal clearly proves the prediction event occurred and the measurement is met.
- SUPPORTED: Signals partially align with the prediction (directionally correct but not definitively confirmed).
- CONTRADICTED: Signals actively indicate the prediction will not happen or the opposite occurred.
- UNCHANGED: No signal is meaningfully relevant to this prediction.

Return ONLY valid JSON:
{{
  "verdict": "CONFIRMED|SUPPORTED|CONTRADICTED|UNCHANGED",
  "matching_signals": ["<Exact signal title 1>", "<Exact signal title 2>"],
  "reasoning": "<One sentence explaining the verdict based only on the signals above.>",
  "confidence": <float 0.0–1.0 representing how confident you are in this verdict>
}}"""

        try:
            response = llm_invoke(self.llm, prompt)
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                result = json.loads(match.group())
                # Validate verdict field
                if result.get("verdict") not in ("CONFIRMED", "SUPPORTED", "CONTRADICTED", "UNCHANGED"):
                    result["verdict"] = "UNCHANGED"
                return result
        except Exception as e:
            logger.error(f"[PredictionTracker] LLM classification failed: {e}")

        return {
            "verdict": "UNCHANGED",
            "matching_signals": [],
            "reasoning": "Failed to parse LLM response.",
            "confidence": 0.0,
        }


def run_prediction_tracking():
    """Entrypoint for the APScheduler job."""
    tracker = PredictionTracker()
    return tracker.run()
