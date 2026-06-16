# Agreement Calculation Methodology

**Status:** PLANNED
**Sprint:** 4.5
**Companion:** calibration_set_v1.md, scoring_template.md, reviewer_instructions.md
**Reference:** resolution_criteria_v1.md (v1.1)
**Output:** feeds calibration_report.md

---

## 1. Goal

Quantify agreement between two independent reviewers on 5 calibration cases, broken down by:
- Overall agreement rate.
- Agreement by resolution class.
- Most common disagreement patterns.
- Per-case agreement.

The output of this methodology is the input to the calibration report.

---

## 2. Inputs

For each case, the calibration lead receives two completed scoring templates:
- Reviewer A: scoring_template_A.md
- Reviewer B: scoring_template_B.md

Each contains:
- Resolution class (one of: CONFIRM, PARTIAL, REJECT, EXPIRED, INVALID_PRECEDED, UNRESOLVABLE)
- Primary source URL(s)
- Secondary source URL(s)
- Notes
- Specific reasoning (Cases 2, 3, 4, 5)

---

## 3. Agreement Definitions

### 3.1 Exact agreement
Both reviewers assign the same resolution class.

Example: Reviewer A = CONFIRM, Reviewer B = CONFIRM → exact agreement.

### 3.2 Adjacent agreement (informational)
Resolution classes that are "close but not equal." Definitions:

- CONFIRM and PARTIAL = adjacent (both positive direction)
- PARTIAL and REJECT = adjacent (PARTIAL = soft positive, REJECT = negative)
- REJECT and EXPIRED = adjacent (EXPIRED treated as REJECT in headline per v1.1 §5.1)

**Note:** Adjacent agreement is **not** counted toward the headline agreement rate. It is reported separately for diagnostic purposes only.

### 3.3 Disagreement
Different resolution classes that are not adjacent by §3.2.

Example: Reviewer A = CONFIRM, Reviewer B = REJECT → disagreement (skips PARTIAL).

---

## 4. Headline Metric

**Overall agreement rate** = count(exact agreements) / count(cases) × 100

- 5 cases total.
- Each case contributes 1 to numerator if exact agreement, 0 otherwise.

### 4.1 Discrete verdict (corrected for N=5)

With N=5, possible agreement rates are quantized to 0%, 20%, 40%, 60%, 80%, 100%. A continuous 85% threshold produces phantom precision.

Verdict is assigned by exact case count, not percentage:

| Verdict | Cases agreed | Action |
|---------|--------------|--------|
| **PASS** | 5/5 | Proceed to 20-company manual resolution pass. Status of v1.1 moves from PLANNED to IMPLEMENTED_NOT_VERIFIED. |
| **BORDERLINE** | 4/5 | Acceptable to proceed, but flag the disagreement case. Conduct targeted v1.2 review on the specific § that drove disagreement. Re-run calibration on the disagreement case only before 20-company pass. |
| **FAIL** | ≤3/5 | Do not proceed to 20-company pass. Document all disagreement patterns. Conduct full v1.2 review with disagreement patterns as input. Re-run full calibration after v1.2 update. |

The percent value is reported for context. The verdict is determined by case count.

---

## 5. Agreement by Resolution Class

For each resolution class (CONFIRM, PARTIAL, REJECT, EXPIRED), count:
- Both reviewers assigned this class (full agreement on class).
- Neither reviewer assigned this class (neither chose it — informational).
- One reviewer assigned, other did not (disagreement involving class).

Report as a matrix:

| Class | Reviewer A | Reviewer B | Agreement on class |
|-------|-----------|-----------|---------------------|
| CONFIRM | N | N | Y/N |
| PARTIAL | N | N | Y/N |
| REJECT | N | N | Y/N |
| EXPIRED | N | N | Y/N |

**Purpose:** identify which classes drive disagreement. If PARTIAL is rarely agreed on, that flags a v1.1 weakness (v1.1's PARTIAL definitions may be underspecified).

---

## 6. Per-Case Agreement

For each of 5 cases, report:
- Reviewer A class.
- Reviewer B class.
- Agreement: YES (exact match) / NO (mismatch).
- Disagreement type: which classes diverged.

Example output table:

| Case | Type | Rev A | Rev B | Exact Agreement | Disagreement Type |
|------|------|-------|-------|-----------------|-------------------|
| 1 | GEO | ... | ... | Y/N | ... |
| 2 | RISK | ... | ... | Y/N | ... |
| 3 | PIVOT | ... | ... | Y/N | ... |
| 4 | MA | ... | ... | Y/N | ... |
| 5 | GEO (ambig) | ... | ... | Y/N | ... |

---

## 7. Disagreement Pattern Taxonomy

For each disagreement, classify the pattern:

### 7.1 Type pattern
Reviewers agree on direction but disagree on whether type classification was correct. E.g., one classified as GEO_EXPANSION, other as VERT_EXPANSION. Different windows may apply.

### 7.2 Window pattern
Reviewers agree on type but disagree on whether event was within horizon. E.g., one says "in window" (180d), other says "out of window" (180d + 4 days).

### 7.3 Source weight pattern
Reviewers agree on event timing but disagree on whether sources are sufficient for CONFIRM vs PARTIAL. E.g., one accepts 1 Primary, other requires 2 Secondary.

### 7.4 Definition pattern
Reviewers apply v1.1 definitions differently. E.g., one interprets PARTIAL as "direction correct, scope off" strictly, other includes "near-horizon events."

### 7.5 Decision test pattern
Reviewers apply v1.1 decision test (e.g., PROD_EXPANSION vs PRODUCT_PIVOT) differently. E.g., one says "Twitter product continued = not PIVOT," other says "company category change = PIVOT."

### 7.6 Unclassifiable
Disagreement does not fit any pattern above. Document in report.

**Each disagreement gets exactly one pattern tag.** If multiple patterns apply, choose the most upstream (earliest in resolution process).

---

## 8. Diagnostic Metrics (Supporting, Not Headline)

### 8.1 Source agreement
For each case, did reviewers cite the same Primary and Secondary sources?
- Full source overlap.
- Partial overlap (some shared, some different).
- No overlap.

### 8.2 Reasoning agreement
Compare the "Specific reasoning" sections for Cases 2, 3, 4, 5. Code as:
- Convergent reasoning (similar logical chain).
- Divergent reasoning (different logic but same conclusion).
- Conflicting reasoning (different logic AND different conclusion).

### 8.3 Confidence in resolution
Did either reviewer flag UNRESOLVABLE or INVALID_PRECEDED? If yes, log and discuss.

---

## 9. Calculation Procedure

Step-by-step:

1. Receive 2 completed scoring templates.
2. Extract resolution class for each of 5 cases from each reviewer.
3. Compute overall agreement rate (count exact matches / 5).
4. Compute per-case agreement.
5. Compute agreement by resolution class (matrix).
6. For each disagreement, assign pattern tag from §7.
7. Compute diagnostic metrics from §8.
8. Produce calibration_report.md.

---

## 10. Output Schema (feeds calibration_report.md)

```yaml
overall_agreement_pct: <0-100>
agreement_threshold_met: <true|false>  # true if >=85%
cases:
  - case_id: CAL-001
    reviewer_a_class: <class>
    reviewer_b_class: <class>
    exact_agreement: <true|false>
    disagreement_pattern: <pattern_tag or null>
  - case_id: CAL-002
    ...
  - case_id: CAL-003
    ...
  - case_id: CAL-004
    ...
  - case_id: CAL-005
    ...
class_agreement_matrix:
  confirm:
    reviewer_a_count: <N>
    reviewer_b_count: <N>
    both_agreed: <N>
  partial:
    ...
  reject:
    ...
  expired:
    ...
disagreement_pattern_summary:
  type_pattern: <count>
  window_pattern: <count>
  source_weight_pattern: <count>
  definition_pattern: <count>
  decision_test_pattern: <count>
  unclassifiable: <count>
diagnostics:
  source_agreement: <full|partial|none per case>
  reasoning_agreement: <convergent|divergent|conflicting per case>
  unresolvable_flags: <count>
verdict: <pass|fail>
next_action: <proceed to 20-company pass | pause for v1.2 review>
```

---

## 11. What This Methodology Does NOT Measure

- Whether v1.1 is "right."
- Whether reviewers are "good."
- Whether Argos is accurate.

It measures: **given v1.1 as written, do two reviewers converge?**

---

## 12. Edge Cases

### 12.1 Reviewer submits UNRESOLVABLE
Treat as its own class. Agreement on UNRESOLVABLE = exact agreement. Disagreement between UNRESOLVABLE and any other class = disagreement, tagged with "definition pattern" (reviewers disagree on resolvability).

### 12.2 Reviewer submits INVALID_PRECEDED
Treat as its own class. Disagreement between INVALID_PRECEDED and any resolution class = disagreement, tagged "definition pattern."

### 12.3 One reviewer submits, other does not
Case excluded from agreement calculation. Flag in report as "non-completion." Multiple non-completions invalidate the calibration.

### 12.4 Late submission
Per v1.1 §6.5: mark DELAYED_RESOLUTION in audit, still count. Flag in report.

---

## 13. Sample-Size Caveat

5 cases is small. N=5 means verdict is quantized to the discrete cases table in §4.1.

- 5/5 = PASS (encouraging, but n=5 means this could be lucky)
- 4/5 = BORDERLINE (acceptable to proceed with flagged case)
- ≤3/5 = FAIL (do not proceed)

**A PASS at 5/5 is encouraging but not statistically robust.** The next validation step (20-company pass) provides the larger sample.

If ≤3/5, do not proceed. Return to v1.1 review with disagreement patterns as input.
