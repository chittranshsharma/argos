# Resolution Criteria v1.1

**Status:** PLANNED
**Version:** 1.1
**Sprint:** 4.5
**Scope:** EXPANSION (5 subtypes), RISK, PRODUCT_PIVOT, M&A
**Supersedes:** v1.0

---

## Changelog v1.0 → v1.1

| Change | Reason |
|--------|--------|
| M&A window: 180d → 365d | Avoid false-rejecting long-cycle deals |
| M&A: added 4-state tracking (discussion / LOI / announced / closed) | Capture progression without inflating confirm rate |
| M&A: only announced/closed resolve; discussions/LOI = PARTIAL | Preserve signal quality, avoid rewarding rumor |
| EXPANSION split into 5 subtypes | Lumping unrelated phenomena corrupted scorecard |
| Partial no longer scored 0.5 | Arbitrary weighting, hides structure |
| Headline metric: Confirm Rate + Lift vs Majority-Class | Composite scores produce arbitrary debates |
| Baseline promoted to first-class metric | "80% accuracy" meaningless without comparison point |
| PRODUCT_EXPANSION vs PRODUCT_PIVOT decision test | Resolve taxonomy overlap |

---

## Definitions Used Throughout

**Resolution** = explicit outcome assigned to a hypothesis. No hypothesis stays "pending" past its resolution window.

**Resolution date** = earliest observable date on which a confirm / reject / partial signal appeared in a public source (press release, SEC filing, company blog, reputable reporting). Internal signals that never surface publicly = effectively "no resolution" and follow special rules below.

**Horizon start** = hypothesis creation date (when Argos first emitted the hypothesis, not when signal was first observed).

**Source classes:**

- **Primary** = company-controlled source (press release, official blog, SEC filing, careers page change, founder tweet from verified account).
- **Secondary** = reputable reporting (TechCrunch, Bloomberg, Reuters, WSJ, FT, The Information, Axios, Semafor).
- **Tertiary** = aggregators, social posts, low-confidence outlets. **Never sufficient alone** to confirm a hypothesis. May trigger reject.

**Two-reviewer rule:** every resolution must be agreed upon by 2 independent reviewers. Disagreement → third reviewer arbitrates. Agreement rate target >85%.

**Frozen record rule:** once a hypothesis is resolved, resolution does not change. Re-classifications require new hypothesis. Subsequent events generate new hypotheses, do not retroactively reclassify old ones.

---

## Taxonomy Overview

| Code | Type | Window |
|------|------|--------|
| `GEO_EXPANSION` | Geographic expansion | 180d |
| `VERT_EXPANSION` | Vertical expansion | 270d |
| `SEG_EXPANSION` | Customer segment expansion | 270d |
| `PROD_EXPANSION` | Product line expansion | 365d |
| `HEAD_EXPANSION` | Headcount tier expansion | 180d |
| `RISK` | Negative event | 90d (180d regulatory, 60d downgrade) |
| `PRODUCT_PIVOT` | Strategic product reorientation | 365d (180d sunset) |
| `MA` | M&A activity | 365d |

**Decision test — PROD_EXPANSION vs PRODUCT_PIVOT:**

- Existing business remains core → `PROD_EXPANSION` (additive growth).
- Existing business ceases to be core or company category changes → `PRODUCT_PIVOT` (strategic replacement).

A product launch can begin as `PROD_EXPANSION` and later become evidence supporting a `PRODUCT_PIVOT` hypothesis, but the same event should not automatically resolve both hypotheses. Each hypothesis resolves independently.

---

## 1. EXPANSION — Split into 5 Subtypes

### 1.1 `GEO_EXPANSION` — Geographic

Predicts: company grows into new country, region, or city.

**Confirm:** new office, new region hiring, new entity registered in new jurisdiction, partnership with local distributor in new market, public announcement of expansion into named market.
**Source:** ≥1 Primary, OR ≥2 independent Secondary.

**Reject:** horizon expires with no observable signal, OR company publicly retreats (closes office, fires leadership in target region, de-prioritizes region).
**Source:** ≥1 Primary or ≥2 Secondary for rejection.

**Partial:** expanded to adjacent but not predicted region (predicted EU → expanded UK only), or wrong scale (predicted 3 offices → opened 1), or timing off >50% of horizon.

**Window:** 180 days.

---

### 1.2 `VERT_EXPANSION` — Vertical

Predicts: company enters new industry vertical.

**Confirm:** public case study, named customer win, or product launch in vertical company was not previously serving. Hiring spike in vertical-specific roles counts as supporting, not sufficient.
**Source:** ≥1 Primary, OR ≥2 independent Secondary.

**Reject:** horizon expires with no observable signal, OR company publicly exits vertical or reaffirms focus on existing verticals.
**Source:** ≥1 Primary or ≥2 Secondary.

**Partial:** entered adjacent vertical (predicted healthcare → entered medtech), or wrong scale, or timing off >50%.

**Window:** 270 days.

---

### 1.3 `SEG_EXPANSION` — Customer Segment

Predicts: company shifts target customer segment (SMB↔Enterprise, consumer↔prosumer, etc.).

**Confirm:** explicit repositioning ("now serving SMB"), pricing tier launch targeting new segment, named customer wins in new segment.
**Source:** ≥1 Primary, OR ≥2 independent Secondary.

**Reject:** horizon expires with no observable signal, OR company publicly reaffirms current segment focus.
**Source:** ≥1 Primary or ≥2 Secondary.

**Partial:** entered segment but did not deprioritize original (e.g., launched SMB tier but enterprise still core), or wrong scale, or timing off >50%.

**Window:** 270 days.

---

### 1.4 `PROD_EXPANSION` — Product Line

Predicts: company launches new product line or SKU as additive growth. Existing business remains core.

**Confirm:** new product SKU launched, new product category launched, new platform launched publicly. Existing product line remains active.
**Source:** ≥1 Primary, OR ≥2 independent Secondary.

**Reject:** horizon expires with no observable launch, OR company publicly cancels planned product.
**Source:** ≥1 Primary or ≥2 Secondary.

**Partial:** product launched as limited/experimental (not core), or wrong scope (predicted "platform" → launched "feature"), or timing off >50%.

**Window:** 365 days.

**Boundary test:** if new product becomes the company's primary offering AND existing product line ceases to be core → this is `PRODUCT_PIVOT`, not `PROD_EXPANSION`. Apply decision test in taxonomy overview.

---

### 1.5 `HEAD_EXPANSION` — Headcount Tier

Predicts: company crosses headcount threshold (e.g., 100→500, 500→1000).

**Confirm:** sustained hiring acceleration >30% over trailing 90-day baseline, with >50 net new roles posted in target function, AND public reference to growth (leadership statement, blog, conference talk).
**Source:** Primary (careers page) + Secondary (reporting on growth) preferred. Either alone with strong signal acceptable.

**Reject:** horizon expires with no observable acceleration, OR company announces hiring freeze or layoffs counter-prediction.
**Source:** ≥1 Primary or ≥2 Secondary.

**Partial:** reached lower tier than predicted (predicted 1000 → reached 750), or timing off >50%.

**Window:** 180 days.

---

## 2. RISK

A hypothesis classified `RISK` predicts: company faces negative event — layoffs, executive departure, hiring freeze, revenue warning, regulatory action, public scandal, downgrade.

### 2.1 Confirm conditions

Any of the following within horizon:

- **Layoffs:** reported in Primary or 2+ Secondary sources, affecting >5% of org or >50 people, or affecting named team.
- **Executive departure:** C-suite or SVP-level departure reported in Primary or 2+ Secondary.
- **Hiring freeze:** explicit public statement, or 60+ days of net-zero postings in previously active department.
- **Revenue warning:** guidance reduction, missed earnings, or explicit warning in earnings call.
- **Regulatory action:** formal filing, lawsuit, or enforcement action in Primary source.
- **Public scandal:** named allegation in Primary or 2+ Secondary, with company response.
- **Downgrade:** credit rating action or sell-side downgrade by named analyst at major firm.

**Source requirement:** Primary OR 2 independent Secondary.

### 2.2 Reject conditions

- Horizon expires with no observable negative signal in predicted category.
- Company publicly demonstrates opposite (record quarter, leadership stability announcement, hiring acceleration).
- Counter-evidence at sufficient weight (e.g., earnings beat by >20% on predicted weakness metric).

**Source requirement:** ≥1 Primary or ≥2 Secondary supporting rejection.

### 2.3 Partial conditions

- Correct category, wrong magnitude (predicted "major layoffs" → small layoffs <2% of org).
- Correct direction, wrong timing by >50% of horizon.
- Predicted risk materializes in adjacent but not predicted category (predicted "executive departure" → regulatory action occurred).

**Partial is not a soft confirm.** It is a first-class outcome that does not contribute to confirm rate.

### 2.4 Resolution window

**Default: 90 days** from hypothesis creation.

**Regulatory action:** 180 days.
**Downgrade:** 60 days.

If no signal in window, classify EXPIRED (see 5.1).

---

## 3. PRODUCT_PIVOT

A hypothesis classified `PRODUCT_PIVOT` predicts: company shifts core product direction, repositions category, or makes fundamental strategic reorientation such that existing business ceases to be core or company category changes.

### 3.1 Confirm conditions

Any of the following within horizon:

- **New product category launched as new primary offering,** with company messaging signaling category shift.
- **Major repositioning:** company changes tagline, ICP messaging, or target market in formal public communication (e.g., earnings call, founder letter, major conference keynote).
- **New technical domain hiring:** sustained hiring (>10 roles over 90 days) in technical domain company did not previously operate in, combined with public signals of capability build.
- **Major product sunset:** discontinuation of previously core product line with public announcement and customer migration plan.

**Source requirement:** ≥1 Primary + ≥1 Secondary, OR ≥3 independent Secondary. Strict threshold.

### 3.2 Reject conditions

- Horizon expires with no observable pivot signal.
- Company doubles down on predicted-to-be-abandoned direction.
- Counter-positioning: company publicly reaffirms current direction in formal communication.

**Source requirement:** Primary OR ≥2 Secondary.

### 3.3 Partial conditions

- Partial pivot: company signals direction shift but does not fully commit (e.g., new product launched as "experiment" or "add-on" rather than core).
- Timing off by >50% of horizon.
- Scope of pivot smaller than predicted.

### 3.4 Resolution window

**Default: 365 days** from hypothesis creation.

**Full product sunset:** 180 days.

If no signal in window → EXPIRED.

---

## 4. M&A

A hypothesis classified `MA` predicts: company acquires, merges with, or is acquired by another named entity.

### 4.1 4-state tracking

| State | Description | Resolves hypothesis? |
|-------|-------------|---------------------|
| `discussion_detected` | Reputable reporting indicates talks underway. | No — evidence only. |
| `LOI_detected` | Letter of intent or exclusive negotiation reported. | No — strong evidence only. |
| `announced` | Formal public announcement by either party. | **Yes — CONFIRM.** |
| `closed` | Deal closes (regulatory approval completed, consideration exchanged). | **Yes — CONFIRM + highest confidence.** |

All 4 timestamps stored per hypothesis for later analysis, but only `announced` and `closed` trigger resolution.

### 4.2 Confirm conditions

- `announced` state reached (formal announcement in Primary source), OR
- `closed` state reached (deal closes per Primary source).

**Source requirement:** Primary (announcement or formal filing) for full confirm.

### 4.3 Reject conditions

- Horizon (365d) expires with no `announced` or `closed` state, AND no `discussion_detected` or `LOI_detected` state.
- Company or target publicly denies.
- Deal definitively falls through (talks end, both parties confirm).

**Source requirement:** Primary OR ≥2 Secondary for denial/fall-through.

### 4.4 Partial conditions

- `discussion_detected` or `LOI_detected` state reached within horizon, but neither `announced` nor `closed` reached before horizon expires.
- Wrong direction: predicted acquirer was actually target, or vice versa.
- Predicted scale wrong (predicted "acquisition" → minority investment occurred).
- Timing off by >50% of horizon.

**Partial is not a soft confirm.** Discussions/LOI alone do not confirm an M&A prediction.

### 4.5 Resolution window

**Default: 365 days** from hypothesis creation.

**Special case — confirmed ongoing discussions:** window extends 90 days from last `discussion_detected` or `LOI_detected` timestamp.

---

## 5. Outcome Scoring Rubric

### 5.1 Resolution classes

| Class | Meaning |
|-------|---------|
| `CONFIRM` | Hypothesis fully confirmed per type-specific rules. |
| `PARTIAL` | Direction correct, scope/timing off per type-specific rules. First-class outcome. |
| `REJECT` | Hypothesis explicitly contradicted within horizon. |
| `EXPIRED` | Horizon passed with no observable signal. Distinguished from REJECT in audit trail; treated as REJECT in headline metrics. |

### 5.2 Headline scorecard metrics

Per hypothesis type, report **separately**:

- `confirm_rate` = count(CONFIRM) / count(resolved)
- `partial_rate` = count(PARTIAL) / count(resolved)
- `reject_rate` = count(REJECT) / count(resolved)
- `expired_rate` = count(EXPIRED) / count(resolved)

**No composite accuracy score.** Partial is not a weighted midpoint of Confirm and Reject. It is a first-class outcome tracked on its own axis.

### 5.3 Lift vs baseline

Headline scorecard shows two numbers per type:

1. `Argos confirm_rate`
2. `Lift vs Majority-Class Baseline` = `Argos confirm_rate − majority_class_baseline`

**Majority-class baseline** = for each hypothesis type, the accuracy a naive system would achieve by always predicting the most-frequent class for that type. Computed on the same resolved set.

Example: if 60% of resolved `RISK` hypotheses are REJECT, majority-class baseline = 60% (always predict REJECT). Argos confirm_rate of 35% → Lift = −25%. Argos confirm_rate of 70% → Lift = +10%.

**Lift is the only number that proves Argos adds predictive value.** Confirm rate alone is uninformative.

### 5.4 Additional baselines (supporting, not headline)

Report alongside headline:

- **In-sample base-rate baseline:** % of companies in resolved set that experienced the event regardless of prediction.
- **External industry baseline:** when available, % of comparable companies that experienced the event per industry data.

External baseline does not block Sprint 4.5. If unavailable, document as UNVERIFIED and continue with majority-class + in-sample.

### 5.5 Required audit fields per resolution

- hypothesis_id
- hypothesis_type (one of 8 codes)
- company
- creation_date
- resolution_date
- resolution_class (CONFIRM / PARTIAL / REJECT / EXPIRED)
- primary_source_url(s)
- secondary_source_url(s)
- reviewer_1_id
- reviewer_2_id
- agreement_flag (TRUE / FALSE)
- notes (free text, max 500 chars)
- criteria_version (must equal "v1.1")
- **M&A only:** timestamps for `discussion_detected`, `LOI_detected`, `announced`, `closed` (any can be null)

### 5.6 Sample size requirements

No accuracy claim is valid unless:

- ≥20 resolved hypotheses per type.
- ≥80 resolved hypotheses system-wide.

Until thresholds met, all metrics = UNVERIFIED.

### 5.7 Frozen-record rule

Once a resolution is recorded, it does not change. Subsequent events do not retroactively reclassify. New events generate new hypotheses.

---

## 6. Human Reviewer Instructions

### 6.1 Reviewer qualification

- Familiar with the company being reviewed.
- Has read the full Resolution Criteria v1.1 document.
- Has completed calibration set of 5 sample resolutions (provided in separate file, not in this doc) with agreement to gold-standard labels.

### 6.2 Review process

1. Open hypothesis record. Read hypothesis text, originating signals, and creation date.
2. Determine hypothesis_type from the 8-code taxonomy. Flag if misclassified — do not re-resolve.
3. Search public sources for relevant events in the resolution window:
   - Start with company official channels (blog, press, careers, founders).
   - Then reputable reporting (TechCrunch, Bloomberg, Reuters, WSJ, FT, The Information).
   - Note search date and queries used.
4. For each candidate signal, classify source as Primary / Secondary / Tertiary.
5. Apply type-specific confirm / partial / reject rules strictly.
6. **For M&A:** record all 4 state timestamps that fired, even if only some fired within window.
7. Record resolution with all required audit fields (5.5).
8. Submit for second reviewer.

### 6.3 Disagreement protocol

- If reviewer 1 and reviewer 2 disagree on resolution class:
  - First, attempt reconciliation in 15-min sync (often one missed a source).
  - If still disagree, escalate to reviewer 3 (arbitrator).
  - Arbitrator decision is final.
  - Log all three positions and reasoning.

### 6.4 Edge cases

- **Hypothesis based on leaked/pre-publication info:** if a public confirmation appeared before the hypothesis creation date, mark `INVALID_PRECEDED`, exclude from accuracy.
- **Hypothesis about a company that ceases to exist (acquired, bankrupt):** resolve as CONFIRM if predicted event caused the end. Otherwise apply normal rules to surviving entity.
- **Conflicting public signals:** weight Primary > Secondary > Tertiary. If Primary sources conflict, prefer most recent, note conflict in audit field.
- **Self-fulfilling hypothesis:** if Argos's published prediction appears to drive the event, mark `POSSIBLE_SELF_FULFILLING` in notes, do not exclude — track separately for analysis.
- **PROD_EXPANSION vs PRODUCT_PIVOT overlap:** apply decision test from taxonomy overview. If unclear, classify as the type the hypothesis was emitted as and flag for review.

### 6.5 Reviewer ethics

- Reviewers must not use insider information.
- Reviewers must not consult Argos's internal confidence scores when resolving.
- Reviewers must complete resolution within 14 days of hypothesis expiration. If exceeded, mark `DELAYED_RESOLUTION`, still count toward metrics but flag in audit.

### 6.6 Calibration maintenance

- Every 20 resolutions, all reviewers re-do 5-sample calibration set.
- Drift >15% from gold-standard = retraining required before resuming.
- Reviewer agreement rate tracked continuously. Below 85% over rolling 50 resolutions = process review.

---

## Change Log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | PLANNED | Initial draft. Superseded. |
| 1.1 | PLANNED | EXPANSION split into 5 subtypes. M&A 365d + 4-state. Partial no longer scored. Baseline promoted. PRODUCT_EXPANSION vs PRODUCT_PIVOT decision test. Awaiting review. |

---

**Reminder:** Status remains PLANNED until reviewed and signed off. Sign-off moves status to IMPLEMENTED_NOT_VERIFIED (document exists, not yet enforced against live hypotheses). Status becomes VERIFIED only after first hypothesis is resolved end-to-end against this document.
