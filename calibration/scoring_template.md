# Scoring Template — Calibration v1.0

**Status:** PLANNED
**Sprint:** 4.5
**Companion:** calibration_set_v1.md, reviewer_instructions.md
**Reference:** resolution_criteria_v1.md (v1.1)
**Reviewer ID:** _________________ (assigned by calibration lead)
**Completion date:** _________________

---

## Reviewer Attestation

I attest that:
- I have read Resolution Criteria v1.1 in full.
- I have read this calibration set in full.
- I have not discussed these cases with the other reviewer.
- I have not consulted Argos internal confidence scores or any other Argos output.
- All resolutions are based solely on v1.1 rules and public sources within the specified horizon.

Signature: _________________  Date: _________________

---

## Case 1 — GEO_EXPANSION (Anthropic Dublin)

**Hypothesis ID:** CAL-001
**Company:** Anthropic
**Creation date (simulated):** 2023-01-15
**Horizon end:** 2023-07-14

### Resolution

**Resolution class:** _________________ (CONFIRM / PARTIAL / REJECT / EXPIRED / INVALID_PRECEDED / UNRESOLVABLE)

**Primary source URL(s):**
1. _________________
2. _________________

**Secondary source URL(s):**
1. _________________
2. _________________

**Search date:** _________________
**Search queries used:** _________________

**Notes (max 500 chars):**
> _________________

**Criteria version:** v1.1

---

## Case 2 — RISK (OpenAI Executive Departure)

**Hypothesis ID:** CAL-002
**Company:** OpenAI
**Creation date (simulated):** 2023-08-15
**Horizon end:** 2023-11-13

### Resolution

**Resolution class:** _________________

**Primary source URL(s):**
1. _________________
2. _________________

**Secondary source URL(s):**
1. _________________
2. _________________

**Search date:** _________________
**Search queries used:** _________________

**Notes (max 500 chars):**
> _________________

**Criteria version:** v1.1

**Specific reasoning required:** apply v1.1 §2.3 timing rule to the 4-day-late event. 4 days = 4.4% of 90-day horizon. Is this within the §2.3 ">50% of horizon" trigger? Document your application of v1.1 §2.1 ("within horizon") to an event 4 days after horizon end.
> _________________

---

## Case 3 — PRODUCT_PIVOT (Twitter → X)

**Hypothesis ID:** CAL-003
**Company:** Twitter / X
**Creation date (simulated):** 2023-04-15
**Horizon end:** 2024-04-14

### Resolution

**Resolution class:** _________________

**Primary source URL(s):**
1. _________________
2. _________________

**Secondary source URL(s):**
1. _________________
2. _________________

**Search date:** _________________
**Search queries used:** _________________

**Notes (max 500 chars):**
> _________________

**Criteria version:** v1.1

**Specific reasoning required:** did the company category change per v1.1 taxonomy decision test? Did existing business cease to be core, OR did company category change (either triggers PRODUCT_PIVOT)?
> _________________

---

## Case 4 — M&A (Microsoft / Activision Blizzard)

**Hypothesis ID:** CAL-004
**Company:** Microsoft / Activision Blizzard
**Creation date (simulated):** 2022-01-10
**Horizon end:** 2023-01-10

### Resolution

**Resolution class:** _________________

**Primary source URL(s):**
1. _________________
2. _________________

**Secondary source URL(s):**
1. _________________
2. _________________

**Search date:** _________________
**Search queries used:** _________________

**Notes (max 500 chars):**
> _________________

**Criteria version:** v1.1

**M&A 4-state timestamps:**
- discussion_detected: _________________ (or null)
- LOI_detected: _________________ (or null)
- announced: _________________ (or null)
- closed: _________________ (or null)

**Specific reasoning required:** did `announced` fire within horizon (2022-01-18 fires before 2023-01-10 horizon end → yes)? Per v1.1 §4.2, does `announced` trigger CONFIRM even though `closed` is after horizon?
> _________________

---

## Case 5 — AMBIGUOUS (Stripe 3 EU Markets)

**Hypothesis ID:** CAL-005
**Company:** Stripe
**Creation date (simulated):** 2023-01-01
**Horizon end:** 2023-09-28

### Resolution

**Resolution class:** _________________

**Primary source URL(s):**
1. _________________
2. _________________

**Secondary source URL(s):**
1. _________________
2. _________________

**Search date:** _________________
**Search queries used:** _________________

**Notes (max 500 chars):**
> _________________

**Criteria version:** v1.1

**Specific reasoning required:** This is the calibration-critical case. Two interpretations:
- **Interpretation A (CONFIRM):** "3 new European markets" was a quantitative claim. Stripe hit 3 (France, Germany, Italy). All continental EU.
- **Interpretation B (PARTIAL):** "With at least one being a country in continental EU" implies specific market expectations. Stripe's chosen markets differ from typical analyst expectations.

Apply v1.1 §1.1 (GEO_EXPANSION) Partial definition strictly: "wrong scale (predicted 3 offices → opened 1)" — scale is exact here. Is the case CONFIRM (scale exact, regions within stated category) or PARTIAL (region set differs from unspecified expectations)?

Document your interpretation:
> _________________

---

## Submission Checklist

- [ ] All 5 cases completed.
- [ ] All required fields filled.
- [ ] Specific reasoning sections answered for Cases 2, 3, 4, 5.
- [ ] Attestation signed.
- [ ] No discussion with other reviewer.

**Submit to:** calibration lead
**Format:** this markdown file, completed.
