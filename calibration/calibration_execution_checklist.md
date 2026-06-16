# Calibration Execution Checklist

**Status:** READY_FOR_CALIBRATION
**Scope:** Two-reviewer calibration on 5 cases

---

## 1. Reviewer Assignment

- [ ] Assign Reviewer A.
- [ ] Assign Reviewer B.
- [ ] Confirm both reviewers have read `resolution_criteria_v1.md`.
- [ ] Confirm both reviewers have read `calibration/reviewer_instructions.md`.
- [ ] Confirm reviewers will work independently and will not discuss cases.
- [ ] Provide each reviewer a separate copy of `calibration/scoring_template.md`.

---

## 2. Completion Requirements

- [ ] All 5 cases completed by each reviewer.
- [ ] One resolution class selected per case.
- [ ] Primary and secondary source URLs documented where used.
- [ ] Search date and search queries documented.
- [ ] Notes completed for each case.
- [ ] Specific reasoning completed for Cases 2, 3, 4, and 5.
- [ ] M&A 4-state timestamps completed for Case 4.
- [ ] Reviewer attestation signed.
- [ ] No invented confidence, accuracy, precision, recall, or performance metrics included.

---

## 3. Agreement Calculation Workflow

- [ ] Receive completed Reviewer A scoring template.
- [ ] Receive completed Reviewer B scoring template.
- [ ] Extract resolution class for all 5 cases from both templates.
- [ ] Count exact agreements out of 5.
- [ ] Calculate overall agreement percentage for context only.
- [ ] Record adjacent agreements separately as informational.
- [ ] Record disagreements and assign one disagreement pattern per disagreement.
- [ ] Complete source agreement diagnostics.
- [ ] Complete reasoning agreement diagnostics.
- [ ] Populate `calibration/calibration_report.md` with real reviewer data only.

---

## 4. Pass / Borderline / Fail Workflow

### PASS

- [ ] Condition: 5/5 exact agreement.
- [ ] Record verdict as PASS.
- [ ] Proceed to 20-company manual resolution pass.

### BORDERLINE

- [ ] Condition: 4/5 exact agreement.
- [ ] Record verdict as BORDERLINE.
- [ ] Flag the disagreement case.
- [ ] Investigate only the section that drove the disagreement.
- [ ] Re-run calibration on the disagreement case before the 20-company pass.

### FAIL

- [ ] Condition: <=3/5 exact agreement.
- [ ] Record verdict as FAIL.
- [ ] Do not proceed to the 20-company manual resolution pass.
- [ ] Document all disagreement patterns.
- [ ] Revise criteria only against the specific defects exposed by reviewer disagreement.
- [ ] Re-run full calibration after revision.

---

## 5. Guardrails

- [ ] Do not fabricate reviewer outputs.
- [ ] Do not simulate agreement results.
- [ ] Do not generate fake metrics.
- [ ] Do not change methodology unless a calibration failure exposes a specific defect.
- [ ] Do not add agents, signals, hypothesis rules, or implementation work during calibration execution.

