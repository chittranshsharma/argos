# Reviewer Instructions — Calibration v1.0

**Status:** READY_FOR_CALIBRATION
**Sprint:** 4.5
**Companion:** calibration_set_v1.md, scoring_template.md
**Reference:** resolution_criteria_v1.md (v1.1) — the only valid reference document
**Required reading order:** Resolution Criteria v1.1 → this document → calibration set → scoring template

---

## 1. Purpose

This calibration measures whether two independent reviewers can apply Resolution Criteria v1.1 to real historical events and produce the same resolution. It does **not** measure whether v1.1 is "right" — it measures whether v1.1 is **consistently interpretable**.

If reviewers converge on **5/5 exact agreement** (PASS), the methodology is validated and we proceed to the 20-company manual resolution pass.

If reviewers converge on **4/5** (BORDERLINE), we proceed with a flag on the disagreement case. If **≤3/5** (FAIL), we pause and revisit v1.1 — but only after documenting the disagreement patterns, not by editing rules ad hoc.

---

## 2. Independence

You must not discuss these cases with the other reviewer. Not in chat, not in person, not in shared notes. Your completed scoring template is the only output you produce.

If you realize after submission that you discussed a case (e.g., overheard), declare it and your submission is excluded from the metric.

The reviewer's job is to produce a resolution per v1.1. The metric is whether two reviewers produce the same resolution.

---

## 3. What You Are Given

For each of 5 cases, the calibration set provides:

- Original hypothesis text (as if Argos had emitted it).
- Time horizon.
- Ground-truth event timeline.
- Source links (Primary and Secondary where applicable).

You may conduct additional research beyond the provided sources. Document any additional sources in the scoring template.

You may **not** use insider information, paid databases behind paywalls not provided, or Argos internal outputs.

---

## 4. What You Produce

For each case, fill out the scoring template with:

1. **Resolution class** — exactly one of: CONFIRM / PARTIAL / REJECT / EXPIRED / INVALID_PRECEDED / UNRESOLVABLE.
2. **Source URLs** — Primary and Secondary used in your determination.
3. **Notes** — short justification, max 500 chars.
4. **Specific reasoning** — for cases 2, 3, 4, 5, additional structured reasoning is required (see scoring template).

---

## 5. Resolution Class Definitions (Reference v1.1 §5.1)

| Class | Meaning |
|-------|---------|
| CONFIRM | Hypothesis fully confirmed per type-specific rules. |
| PARTIAL | Direction correct, scope/timing off per type-specific rules. First-class outcome. |
| REJECT | Hypothesis explicitly contradicted within horizon. |
| EXPIRED | Horizon passed with no observable signal. Distinguished from REJECT in audit; treated as REJECT in headline. |
| INVALID_PRECEDED | Public confirmation appeared before hypothesis creation date. Exclude from metric. |
| UNRESOLVABLE | Insufficient public information to resolve. Flag for calibration lead review. |

You are not required to use INVALID_PRECEDED or UNRESOLVABLE. If you do, document why in notes.

---

## 6. Source Classes (Reference v1.1 Definitions)

- **Primary** = company-controlled source (press release, official blog, SEC filing, careers page change, founder tweet from verified account).
- **Secondary** = reputable reporting (TechCrunch, Bloomberg, Reuters, WSJ, FT, The Information, Axios, Semafor).
- **Tertiary** = aggregators, social posts, low-confidence outlets. Never sufficient alone.

For a CONFIRM or REJECT, v1.1 requires either ≥1 Primary OR ≥2 independent Secondary sources. Tertiary alone is insufficient.

If you cannot find a Primary or 2 Secondary supporting your resolution, you should reconsider before submitting.

---

## 7. Per-Case Application

### Case 1 — GEO_EXPANSION (Anthropic Dublin)
Apply v1.1 §1.1 strictly. Source requirement: ≥1 Primary or ≥2 Secondary.

### Case 2 — RISK (OpenAI Executive Departure)
Apply v1.1 §2.1 (executive departure subcategory). Source requirement: ≥1 Primary or ≥2 Secondary.

Timing process: identify the horizon end and the event date. Apply v1.1 §2.1 ("within horizon") and v1.1 §2.3 ("wrong timing by >50% of horizon") as written. Document your interpretation and final resolution without inferring any preferred answer.

### Case 3 — PRODUCT_PIVOT (Twitter → X)
Apply v1.1 §3.1 strictly. The decision test from v1.1 taxonomy overview applies: did existing business cease to be core, or did company category change?

Source requirement: ≥1 Primary + ≥1 Secondary, OR ≥3 independent Secondary. **Strictest threshold of any type.**

### Case 4 — M&A (Microsoft / Activision Blizzard)
Apply v1.1 §4 strictly. Use the 4-state model.

Critical dates to evaluate: 2022-01-18 is the announcement date. 2022-01-10 is the simulated hypothesis creation date. 2023-01-10 is the horizon end. 2023-10-13 is the close date. Apply v1.1 §4.2 to determine whether `announced` or `closed` resolves the hypothesis.

Source requirement: Primary (announcement or formal filing) for full confirm.

### Case 5 — AMBIGUOUS (Stripe 3 EU Markets)
Apply v1.1 §1.1 strictly to the hypothesis text and ground-truth timeline.

The hypothesis text specifies "3 European markets" — you must interpret this against the actual outcome. Apply v1.1 definitions, determine the appropriate resolution class, and document your reasoning.

The ground truth timeline tells you what actually happened. Your job is to resolve against v1.1 rules, not to debate whether the original prediction was well-stated.

Document any ambiguity in the hypothesis text, type assignment, window selection, or scale interpretation. The metric measures whether reviewers apply v1.1 consistently.

---

## 8. What If You're Unsure

Apply v1.1 strict reading. If v1.1 is silent on your edge case, document the gap in notes. Do not invent rules.

If a case is genuinely unresolvable from public information, mark UNRESOLVABLE and explain.

If a case has a resolution that depends on a judgment call not pinned down by v1.1, make the call and document your reasoning explicitly. This is valuable calibration data — it surfaces where v1.1 needs sharpening.

---

## 9. After Submission

You will not see the other reviewer's submission. The calibration lead will:

1. Compare your resolutions to the other reviewer's.
2. Compute agreement metrics (see agreement_methodology.md).
3. Produce calibration_report.md.

You will see the calibration report once complete. It will not attribute specific answers to specific reviewers.

---

## 10. Timeline

You have **7 days** from receiving this package to submit. If you cannot complete in 7 days, notify calibration lead before day 5. Late submissions are flagged DELAYED_RESOLUTION per v1.1 §6.5 and still count toward metrics.

---

## 11. What This Calibration Does NOT Measure

- Whether v1.1 is "right" in an absolute sense.
- Whether Argos's actual hypotheses will be accurate.
- Whether the hypothesis types are the right taxonomy.
- Whether the horizon windows are optimal.

It measures only: **given v1.1 as written, can two reviewers converge on the same resolution?**

---

## 12. Questions

If something in v1.1 or this package is unclear, ask the calibration lead **before** starting your review. Do not interpret ambiguity in v1.1 by consulting other reviewers or external sources. Document the question and the lead's answer in your notes for the case.
