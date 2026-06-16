# Calibration Report v1.0

**Status:** READY_FOR_CALIBRATION — template awaiting real reviewer data
**Sprint:** 4.5
**Date of report:** _________________
**Calibration lead:** _________________
**Reviewers:** _________________ (anonymized in this report)
**Companion docs:** calibration_set_v1.md, scoring_template.md, reviewer_instructions.md, agreement_methodology.md
**Reference:** resolution_criteria_v1.md (v1.1)

---

## 1. Executive Summary

**Status:** _________________ (PASS / FAIL / BORDERLINE)

**Overall agreement rate:** ____% (reported for context; verdict determined by case count)

**Verdict on methodology:** _________________

**Recommended next step:** _________________

---

## 2. Headline Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Overall agreement rate | ____% | — | — |
| Cases with exact agreement | __/5 | 5/5 = PASS / 4/5 = BORDERLINE / ≤3/5 = FAIL | ✓ / ✗ |
| Cases with adjacent agreement | __/5 | informational | — |
| Cases with disagreement | __/5 | — | — |

---

## 3. Per-Case Results

### Case 1 — GEO_EXPANSION (Anthropic Dublin)

| Field | Value |
|-------|-------|
| Reviewer A class | _________________ |
| Reviewer B class | _________________ |
| Exact agreement | YES / NO |
| Disagreement pattern (if NO) | _________________ |
| Source agreement | full / partial / none |
| Reasoning agreement | convergent / divergent / conflicting |

**Reviewer A notes:** _________________
**Reviewer B notes:** _________________

**Analysis:** _________________

---

### Case 2 — RISK (OpenAI Executive Departure)

| Field | Value |
|-------|-------|
| Reviewer A class | _________________ |
| Reviewer B class | _________________ |
| Exact agreement | YES / NO |
| Disagreement pattern (if NO) | _________________ |
| Source agreement | full / partial / none |
| Reasoning agreement | convergent / divergent / conflicting |

**Reviewer A specific reasoning:** _________________
**Reviewer B specific reasoning:** _________________

**Analysis:** _________________

---

### Case 3 — PRODUCT_PIVOT (Twitter → X)

| Field | Value |
|-------|-------|
| Reviewer A class | _________________ |
| Reviewer B class | _________________ |
| Exact agreement | YES / NO |
| Disagreement pattern (if NO) | _________________ |
| Source agreement | full / partial / none |
| Reasoning agreement | convergent / divergent / conflicting |

**Reviewer A specific reasoning:** _________________
**Reviewer B specific reasoning:** _________________

**Analysis:** _________________

---

### Case 4 — M&A (Microsoft / Activision Blizzard)

| Field | Value |
|-------|-------|
| Reviewer A class | _________________ |
| Reviewer B class | _________________ |
| Exact agreement | YES / NO |
| Disagreement pattern (if NO) | _________________ |
| Source agreement | full / partial / none |
| Reasoning agreement | convergent / divergent / conflicting |
| 4-state timestamps (A) | discussion: ___ / LOI: ___ / announced: ___ / closed: ___ |
| 4-state timestamps (B) | discussion: ___ / LOI: ___ / announced: ___ / closed: ___ |

**Analysis:** _________________

---

### Case 5 — AMBIGUOUS (Stripe 3 EU Markets)

| Field | Value |
|-------|-------|
| Reviewer A class | _________________ |
| Reviewer B class | _________________ |
| Exact agreement | YES / NO |
| Disagreement pattern (if NO) | _________________ |
| Source agreement | full / partial / none |
| Reasoning agreement | convergent / divergent / conflicting |

**Reviewer A specific reasoning:** _________________
**Reviewer B specific reasoning:** _________________

**Analysis:** _________________

---

## 4. Agreement by Resolution Class

| Class | Reviewer A count | Reviewer B count | Both agreed on | One chose, other didn't |
|-------|------------------|------------------|----------------|------------------------|
| CONFIRM | __ | __ | __ | __ |
| PARTIAL | __ | __ | __ | __ |
| REJECT | __ | __ | __ | __ |
| EXPIRED | __ | __ | __ | __ |
| INVALID_PRECEDED | __ | __ | __ | __ |
| UNRESOLVABLE | __ | __ | __ | __ |

**Insight:** _________________

---

## 5. Disagreement Pattern Summary

| Pattern | Count | % of disagreements |
|---------|-------|-------------------|
| Type pattern (disagreement on type classification) | __ | __% |
| Window pattern (disagreement on within-horizon) | __ | __% |
| Source weight pattern (disagreement on source sufficiency) | __ | __% |
| Definition pattern (disagreement on PARTIAL/REJECT/EXPIRED definitions) | __ | __% |
| Decision test pattern (disagreement on decision test application) | __ | __% |
| Unclassifiable | __ | __% |

**Most common pattern:** _________________

**Insight:** _________________

---

## 6. Diagnostics

### 6.1 Source agreement distribution

- Full source overlap: __/5 cases
- Partial overlap: __/5 cases
- No overlap: __/5 cases

### 6.2 Reasoning agreement

- Convergent reasoning: __/5 cases
- Divergent reasoning: __/5 cases
- Conflicting reasoning: __/5 cases

### 6.3 Special flags

- UNRESOLVABLE flags: __
- INVALID_PRECEDED flags: __
- DELAYED_RESOLUTION flags: __
- Non-completions: __

---

## 7. Insights on V1.1

**Where v1.1 produced convergent interpretations:**
> _________________

**Where v1.1 produced divergent interpretations:**
> _________________

**Specific v1.1 sections that drove disagreement (cite by §):**
> _________________

**Whether v1.1 wording is the source of disagreement or whether reviewer judgment is the source:**
> _________________

---

## 8. Verdict and Recommendation

### 8.1 Verdict

**Cases with exact agreement:** __/5
**Verdict:** PASS (5/5) / BORDERLINE (4/5) / FAIL (≤3/5)

### 8.2 Recommendation

**If PASS (5/5):**
- Proceed to 20-company manual resolution pass.
- Status of Resolution Criteria v1.1 moves from PLANNED to IMPLEMENTED_NOT_VERIFIED.
- Begin schema design for hypothesis → resolution tracking.

**If BORDERLINE (4/5):**
- Acceptable to proceed, but flag the disagreement case.
- Conduct targeted v1.2 review on the specific § that drove disagreement.
- Re-run calibration on the disagreement case only before 20-company pass.

**If FAIL (≤3/5):**
- Do not proceed to 20-company pass.
- Document all disagreement patterns in this report.
- Conduct full v1.2 review with disagreement patterns as input.
- Re-run full calibration after v1.2 update.

### 8.3 Specific recommended actions

1. _________________
2. _________________
3. _________________

---

## 9. Next Steps (After This Report)

| Step | Owner | Target Date | Status |
|------|-------|-------------|--------|
| _________________ | _________________ | _________________ | pending |
| _________________ | _________________ | _________________ | pending |
| _________________ | _________________ | _________________ | pending |

---

## 10. Appendices

### Appendix A — Reviewer A scoring template (redacted of identifying info)
[attached]

### Appendix B — Reviewer B scoring template (redacted of identifying info)
[attached]

### Appendix C — Raw agreement data
[attached as YAML per agreement_methodology.md §10]

### Appendix D — Source links cited by reviewers
[attached]

---

## Change Log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | PLANNED | Initial template. Awaiting real reviewer data. |

---

**Reminder:** This report remains PLANNED until both reviewer scoring templates are received. Do not produce an "interim" or "estimated" agreement rate — that would violate the testing rules against invented metrics.
