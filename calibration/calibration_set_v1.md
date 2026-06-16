# Calibration Set v1.0

**Status:** PLANNED
**Sprint:** 4.5
**Companion:** reviewer_instructions.md, scoring_template.md
**Reference:** resolution_criteria_v1.md (v1.1)
**Reviewer scope:** 5 cases. Use v1.1 only.

---

## Setup

Each case is presented as if Argos had emitted the hypothesis on the creation date below. The horizon is the period during which v1.1 rules must be applied. The ground-truth event timeline is provided so reviewers can apply v1.1 to the same facts.

You may consult additional public sources. Document them in the scoring template.

---

## Case 1 — GEO_EXPANSION (Anthropic Dublin)

### Hypothesis

> "Anthropic will open its first European office in Dublin, Ireland, to serve as its EMEA headquarters, within 180 days."

**Hypothesis ID:** CAL-001
**Hypothesis type:** `GEO_EXPANSION` (v1.1 §1.1)
**Company:** Anthropic
**Creation date (simulated):** 2023-01-15
**Horizon end:** 2023-07-14 (180 days, per v1.1 §1.1.4)
**Region predicted:** Dublin, Ireland (EMEA hub)

### Ground-Truth Event Timeline

- 2023-05-19: Anthropic announces Dublin office opening, 30+ jobs initially, EMEA HQ. Press release on anthropic.com.
- 2023-05-19: Reuters, Bloomberg, TechCrunch, FT all cover.
- 2023-09 onwards: office operational, additional hiring.

### Provided Sources

**Primary:**
- https://www.anthropic.com/news/anthropic-europe (Anthropic blog, official)

**Secondary:**
- https://www.reuters.com/technology/anthropic-dublin-office-2023-05-19/
- https://www.bloomberg.com/news/articles/2023-05-19/anthropic-dublin
- https://techcrunch.com/2023/05/19/anthropic-european-hub-dublin/

### V1.1 Question to Resolve

Apply v1.1 §1.1:
- **Confirm:** new office, new region hiring, partnership with local distributor, public announcement of expansion into named market. ≥1 Primary or ≥2 independent Secondary.
- **Partial:** wrong scale, wrong scope (Dublin vs. broader EU), or timing off >50% of horizon (90 days late is 50% — May 19 is ~4 months after creation, ~123 days, ~68% of horizon — does this count as "timing off >50%"?).
- **Reject:** horizon expires with no observable signal, or company publicly retreats.
- **EXPIRED:** horizon (2023-07-14) expires with no signal. **Not applicable here — event fired 2023-05-19, before horizon end.**

### Notes for Reviewer

This is a **control CONFIRM case**. The event fired within the prediction window (2023-05-19, before horizon end 2023-07-14). Per v1.1 §1.1.1 confirm conditions, the new office and EMEA HQ public announcement meet the bar with Primary source (Anthropic blog) and multiple Secondary sources (Reuters, Bloomberg, TechCrunch, FT).

v1.1 §1.1.3 PARTIAL trigger "wrong timing by >50% of horizon" refers to **timing deviation from the prediction window**, not "elapsed fraction of horizon at the time of event." Since the event occurred within the window (before 2023-07-14), the PARTIAL timing trigger does not apply.

This case is included to verify that reviewers apply the control-resolution path correctly. Expected resolution: CONFIRM.

---

## Case 2 — RISK (OpenAI Executive Departure)

### Hypothesis

> "OpenAI's CEO will depart or be removed from the role within 90 days."

**Hypothesis ID:** CAL-002
**Hypothesis type:** `RISK` (v1.1 §2.1, executive departure subcategory)
**Company:** OpenAI
**Creation date (simulated):** 2023-08-15
**Horizon end:** 2023-11-13 (90 days, per v1.1 §2.4)
**Risk category predicted:** Executive departure (C-suite level)

### Ground-Truth Event Timeline

- 2023-11-17 12:21 PT: OpenAI blog post — "Sam Altman Removed from OpenAI Board." Confirmed by multiple sources same day.
- 2023-11-17: Mira Murati appointed interim CEO.
- 2023-11-20: Emmett Shear appointed interim CEO.
- 2023-11-22: Sam Altman returns as CEO, new board announced.

### Provided Sources

**Primary:**
- https://openai.com/blog/sam-altman-removed-from-board (OpenAI official blog)
- OpenAI internal memo leaks (not company-controlled but widely reported; treat as Primary only if from OpenAI-controlled channel)

**Secondary:**
- https://www.reuters.com/technology/openai-ceo-altman-2023-11-17/
- https://www.bloomberg.com/news/articles/2023-11-17/openai-altman-removed
- https://techcrunch.com/2023/11/17/sam-altman-openai-board/
- https://www.theinformation.com/articles/openai-altman-ouster

### V1.1 Question to Resolve

- **Horizon:** 2023-11-13. Event: 2023-11-17. Event is **4 days after horizon end.**
- 4 days = 4.4% of 90-day horizon. Under v1.1 §2.3 PARTIAL trigger (">50% of horizon"). 4 days is **not** >50%.
- 4 days past horizon is **not** "within horizon" per v1.1 §2.1 ("Any of the following within horizon").

Two valid interpretations:
- **Interpretation A (REJECT):** Event occurred 4 days after horizon end. Strict reading of "within horizon" → REJECT.
- **Interpretation B (PARTIAL):** v1.1 §2.3 PARTIAL "wrong timing by >50% of horizon" — 4 days is not >50%. But PARTIAL may apply for "event occurred just outside horizon" reasoning. v1.1 does not explicitly cover this case.
- **Interpretation C (EXPIRED):** Horizon passed with no observable signal at 2023-11-13. By 2023-11-13, the departure had not yet happened. Treat as EXPIRED. **Note:** EXPIRED is treated as REJECT in headline metrics per v1.1 §5.1.

### Notes for Reviewer

This is a deliberately tight-edge test. The "right" resolution depends on v1.1 strictness.

- If v1.1 §2.1 "within horizon" is read strictly, the answer is REJECT or EXPIRED.
- If v1.1 §2.3 PARTIAL "wrong timing by >50%" is the only PARTIAL trigger for RISK, then 4 days does not trigger PARTIAL — meaning the answer is REJECT/EXPIRED, not PARTIAL.
- If the v1.1 author intended "near-horizon event" to count as PARTIAL, that intent is not stated explicitly in v1.1.

**Note for calibration:** Document your interpretation explicitly. This is a v1.1 ambiguity test.

---

## Case 3 — PRODUCT_PIVOT (Twitter → X)

### Hypothesis

> "Twitter will undergo a major repositioning such that the company's primary product category changes within 365 days."

**Hypothesis ID:** CAL-003
**Hypothesis type:** `PRODUCT_PIVOT` (v1.1 §3.1)
**Company:** Twitter, Inc. (later X Corp.)
**Creation date (simulated):** 2023-04-15
**Horizon end:** 2024-04-14 (365 days, per v1.1 §3.4)
**Category change predicted:** "Primary product category changes"

### Ground-Truth Event Timeline

- 2023-07-23: Twitter rebrand to X announced. Logo change. Domain x.com activated (links to twitter.com at this stage).
- 2023-07-23: Elon Musk posts on X (formerly Twitter) announcing rebrand.
- 2023-09 onwards: gradual migration to x.com domain.
- 2024 onwards: xAI integration, "everything app" positioning. Company legally renamed to X Corp.
- Twitter the social network continues to operate as the core product throughout.

### Provided Sources

**Primary:**
- https://twitter.com/elonmusk/status/1683943861479522304 (verified founder post)
- https://about.twitter.com/en/change.html (Twitter official change page) [URL may have changed post-rebrand]
- https://x.com (domain activation)

**Secondary:**
- https://www.reuters.com/technology/twitter-rebrand-x-2023-07-23/
- https://www.bloomberg.com/news/articles/2023-07-23/twitter-x-rebrand
- https://techcrunch.com/2023/07/23/twitter-x-rebrand/
- https://www.wsj.com/articles/twitter-changes-name-to-x-6e8c8e3c

### V1.1 Question to Resolve

Apply v1.1 §3.1 + decision test from taxonomy overview:
- **PRODUCT_PIVOT triggers if:** existing business ceases to be core, OR company category changes.
- **Twitter → X:** social network (the product) continued operating. Brand and corporate name changed. "X" branded as "everything app" / "super app" but Twitter the social network remained the dominant product throughout the horizon.

Two valid interpretations:
- **Interpretation A (CONFIRM):** "Primary product category changes" — X branding explicitly positioned the company as broader than social (financial services, communications, AI). CEO statements support this. Per v1.1 §3.1 ("Major repositioning: company changes tagline, ICP messaging"), CONFIRM.
- **Interpretation B (PARTIAL):** "Strategic reorientation such that existing business ceases to be core" — Twitter the social network remained core. Brand changed, but product category did not. The decision test (existing business ceases to be core) is not met. PARTIAL for direction correct, scope not full.
- **Interpretation C (REJECT):** Twitter the social network continued as core. Existing business did not cease to be core. No category change in product sense. Strict reading → REJECT.

### Notes for Reviewer

This is a v1.1 decision-test test. The decision test from the taxonomy overview is the key:
> "Existing business ceases to be core → PRODUCT_PIVOT."

Twitter the social network did not cease to be core. Strict reading → not PRODUCT_PIVOT by decision test. But v1.1 §3.1 also lists "Major repositioning" as a confirm trigger, which may apply even when the existing product is not abandoned.

**Note for calibration:** This is a v1.1 internal-tension test. v1.1 §3.1 ("major repositioning") and the taxonomy decision test (existing business ceases to be core) may conflict. Document your interpretation. This is the highest-value calibration case for surfacing v1.1 weaknesses.

---

## Case 4 — M&A (Microsoft / Activision Blizzard)

### Hypothesis

> "Microsoft will announce a definitive agreement to acquire Activision Blizzard for ~$68.7B within 365 days."

**Hypothesis ID:** CAL-004
**Hypothesis type:** `MA` (v1.1 §4)
**Company:** Microsoft / Activision Blizzard
**Creation date (simulated):** 2022-01-10
**Horizon end:** 2023-01-10 (365 days, per v1.1 §4.5)
**Acquirer predicted:** Microsoft
**Target predicted:** Activision Blizzard
**Consideration predicted:** ~$68.7B

### Ground-Truth Event Timeline

- 2022-01-18: Microsoft announces definitive agreement to acquire Activision Blizzard for $68.7B. Press release on microsoft.com and activisionblizzard.com.
- 2022-01-18: SEC 8-K filings by both companies.
- 2022-2023: Regulatory review (FTC, EU CMA, UK CMA).
- 2023-07: UK CMA blocks deal initially.
- 2023-10-13: Deal closes after UK CMA approval with restructured terms (cloud streaming rights sold to Ubisoft).

### Provided Sources

**Primary:**
- https://news.microsoft.com/2022/01/18/microsoft-to-acquire-activision-blizzard/ (Microsoft official)
- https://www.activisionblizzard.com/press-releases (Activision Blizzard official)
- SEC 8-K filings, 2022-01-18

**Secondary:**
- https://www.reuters.com/technology/microsoft-activision-deal-2022-01-18/
- https://www.bloomberg.com/news/articles/2022-01-18/microsoft-activision-blizzard-deal
- https://www.wsj.com/articles/microsoft-activision-blizzard-deal-11642556142
- https://www.ft.com/content/27b5e3a8-7a6a-4d8e-9e2b-7e9b9b9b9b9b (FT coverage)

### V1.1 Question to Resolve

Apply v1.1 §4 strictly with 4-state model:
- **discussion_detected:** Likely October 2021 (reports of Microsoft interest). Within horizon start. May be relevant.
- **LOI_detected:** Not publicly reported with date. Mark null or discuss.
- **announced:** 2022-01-18. **Within horizon (2023-01-10 end).** Triggers CONFIRM per v1.1 §4.2.
- **closed:** 2023-10-13. **After horizon end.** Does not affect resolution since `announced` already triggered.

**Resolution:** Should be CONFIRM, since `announced` fired within horizon.

Source requirement: Primary (announcement) for full confirm. Multiple Primary sources present.

### Notes for Reviewer

This is a "clean" M&A case — the v1.1 4-state model applies cleanly. Expected resolution: CONFIRM.

Use this case to validate that the 4-state tracking works as designed. Record all 4 timestamps, even if some are null.

---

## Case 5 — AMBIGUOUS (Stripe EU Markets)

### Hypothesis

> "Stripe will expand into 3 new European Union markets within 270 days."

**Hypothesis ID:** CAL-005
**Hypothesis type:** `GEO_EXPANSION` (v1.1 §1.1)
**Company:** Stripe
**Creation date (simulated):** 2023-01-01
**Horizon end:** 2023-09-28 (270 days, per v1.1 §1.2 — note: VERT/SEG use 270, GEO uses 180; this case uses 270 because the analyst who emitted it classified it as a multi-region expansion, not pure GEO. **Reviewer must determine correct type from v1.1 rules and apply correct window.**)
**Region predicted:** 3 EU markets, unspecified

### Ground-Truth Event Timeline

- 2023-02-15: Stripe announces expansion into **Italy** via partnership with local banks.
- 2023-05-09: Stripe announces expansion into **France**.
- 2023-07-19: Stripe announces expansion into **Greece**.
- (Earlier in 2022, Stripe had already expanded into **Germany** and several other EU markets.)

### Provided Sources

**Primary:**
- https://stripe.com/blog/payments-italy (Stripe blog, 2023-02-15)
- https://stripe.com/blog/payments-france (Stripe blog, 2023-05-09)
- https://stripe.com/blog/payments-greece (Stripe blog, 2023-07-19)

**Secondary:**
- https://techcrunch.com/2023/07/19/stripe-greece/
- https://www.reuters.com/technology/stripe-eu-2023/

### V1.1 Question to Resolve

**Question 1 — type assignment:**
Hypothesis says "3 new European Union markets." v1.1 has two relevant types:
- `GEO_EXPANSION` (window 180d)
- (Possibly `VERT_EXPANSION` if "markets" interpreted as verticals, but "European Union markets" is geographic language → GEO_EXPANSION)

Strict reading: GEO_EXPANSION, 180-day window. Horizon end: **2023-06-30** (not 2023-09-28 as initially written).

This changes the resolution. Let us apply both:

**If 180-day window (2023-06-30):**
- Italy (2023-02-15): within window ✓
- France (2023-05-09): within window ✓
- Greece (2023-07-19): outside window ✗
- Within window: 2 of 3. v1.1 §1.1.3 PARTIAL ("wrong scale: predicted 3 → opened 2" — but 2 of 3 is borderline).

**If 270-day window (2023-09-28):**
- Italy, France, Greece: all within window ✓
- 3 of 3 confirmed.
- v1.1 §1.1.1 CONFIRM.

**Question 2 — what counts as "new":**
Germany was expanded in 2022, before hypothesis creation. Not new in 2023. Italy, France, Greece in 2023 = new.

Two interpretations:
- **Interpretation A (CONFIRM via 270d):** 3 markets launched within 270 days. v1.1 §1.1.1 CONFIRM.
- **Interpretation B (PARTIAL via 180d):** Only 2 markets launched within 180 days. v1.1 §1.1.3 PARTIAL ("wrong scale: predicted 3 → got 2").
- **Interpretation C (CONFIRM via 180d, different market set):** If "European Union markets" was interpreted as continental EU specifically, and Italy + France are confirmed continental EU but Greece is borderline (Greece is EU but some readers might interpret as different region), then 2 of 3 confirmed → PARTIAL.

### Notes for Reviewer

This is the **calibration-critical case** for testing PARTIAL vs CONFIRM interpretation.

Key v1.1 questions:
1. Should the reviewer independently select the type (and thus the window) from the hypothesis text, or accept the type assigned in the calibration case?
2. If the hypothesis text is ambiguous between "3 markets" and "3 specific markets" (the latter implying particular analyst expectations), how should this be resolved?
3. Is the v1.1 §1.1.3 PARTIAL trigger "wrong scale (predicted 3 offices → opened 1)" interpreted as strict numeric (3 ≠ 2 triggers PARTIAL) or as rough magnitude (within 1 unit = scale approximately correct)?

**Note for calibration:** This case is designed to surface PARTIAL vs CONFIRM interpretation differences. The "right" answer depends on v1.1 strictness on numeric scale, which v1.1 does not explicitly address. The two reviewers may legitimately disagree, and that disagreement is the calibration data we want.

---

## Summary Table

| Case | Type | Horizon | Expected resolution (calibration lead hypothesis) |
|------|------|---------|--------------------------------------------------|
| 1 | GEO_EXPANSION | 180d | CONFIRM (control case — event within window, Primary + multiple Secondary) |
| 2 | RISK | 90d | REJECT/EXPIRED (4 days past horizon) OR PARTIAL (if v1.1 §2.3 "wrong timing" includes near-misses) |
| 3 | PRODUCT_PIVOT | 365d | CONFIRM (repositioning is §3.1 trigger) OR PARTIAL (Twitter product continued, decision test fails) OR REJECT (strict decision test) |
| 4 | MA | 365d | CONFIRM (announced 2022-01-18 within horizon) |
| 5 | GEO_EXPANSION | 180d or 270d | CONFIRM (3 of 3 in 270d) OR PARTIAL (2 of 3 in 180d strict numeric) |

**Calibration objective:** measure whether reviewers converge on these (or other) interpretations. Disagreement is expected on Cases 2, 3, and 5. Cases 1 and 4 are control CONFIRM cases — reviewer convergence on CONFIRM is the calibration data we want for those.

**Note for calibration lead:** "Expected resolution" rows are the calibration lead's pre-test hypothesis for diagnostic purposes only. They are not communicated to reviewers. Reviewers apply v1.1 independently.
