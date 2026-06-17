"""
Sprint D — Hypothesis Generation Quality
Runs the HypothesisEngine against all companies using stored signals,
then grades the output and produces Hypothesis Quality Report v1.

Do not modify validator logic.
Do not add new audit frameworks.
"""

import json
import re
import time
import csv
from collections import defaultdict
from datetime import datetime, timezone

from app.database import get_supabase_client
from app.analysis.hypothesis_engine import HypothesisEngine
from app.llm import get_groq_llm, llm_invoke

client = get_supabase_client()
llm = get_groq_llm()

GRADE_PROMPT = """You are a strategic intelligence analyst grading a generated hypothesis.

Company: {company_name}
Belief: {title}
Description: {description}
Confidence: {confidence}

Grade using this rubric (choose ONE letter only):
A = Decision-changing insight — a CEO could act on this immediately, it stakes a bold and specific claim
B = Useful synthesis — combines signals in a non-obvious way, directionally useful
C = Accurate summary — correctly describes company behaviour but adds no new framing
D = Generic observation — true of most companies in the sector, not specific to this company
F = Noise — vague, contradicted by evidence, or strategically empty

Also score 1-5:
- specificity: How specific is this to THIS company vs any company in the sector?
- novelty: How non-obvious is the insight given the raw signals?
- actionability: Could an analyst or investor act on this today?

Return ONLY valid JSON:
{{
  "grade": "A|B|C|D|F",
  "specificity": <int 1-5>,
  "novelty": <int 1-5>,
  "actionability": <int 1-5>,
  "reasoning": "<one sentence explanation>"
}}"""

def grade_hypothesis(h: dict, company_name: str) -> dict | None:
    prompt = GRADE_PROMPT.format(
        company_name=company_name,
        title=h.get("title", ""),
        description=(h.get("description", "") or "")[:600],
        confidence=h.get("confidence", 0)
    )
    try:
        resp = llm_invoke(llm, prompt)
        match = re.search(r"\{.*\}", resp, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  [GRADE ERROR] {e}")
    return None


def run_generation_for_company(company: dict, all_signals: list) -> dict:
    """Feed stored signals through the HypothesisEngine for one company."""
    company_id = company["id"]
    company_name = company["name"]

    print(f"\n{'='*55}")
    print(f"  {company_name} ({len(all_signals)} signals)")
    print(f"{'='*55}")

    if not all_signals:
        print("  No signals — skipping.")
        return {"company": company_name, "hypotheses_created": 0, "hypotheses": []}

    try:
        engine = HypothesisEngine()
        # Run on ALL stored signals; engine handles deduplication internally
        engine.generate_hypotheses(
            company_id=company_id,
            company_name=company_name,
            recent_signals=all_signals,
            trigger_reason="Sprint D — bulk quality measurement run"
        )
        metrics = engine.metrics
        print(f"  Created: {metrics['hypotheses_created']}  "
              f"Deduplicated: {metrics['hypotheses_deduplicated']}  "
              f"Rejection rate: {metrics['quality_rejection_rate']}")
        return {"company": company_name, "metrics": metrics}
    except Exception as e:
        print(f"  [ENGINE ERROR] {e}")
        return {"company": company_name, "error": str(e)}


def main():
    print("=" * 55)
    print("  Sprint D — Hypothesis Generation Quality Run")
    print("=" * 55)

    # 1. Fetch all companies + their signals
    companies = client.table("companies").select("*").execute().data or []
    print(f"\nCompanies in DB: {len(companies)}")

    company_signal_map = {}
    for co in companies:
        sigs = client.table("signals").select("*").eq("company_id", co["id"]).execute().data or []
        company_signal_map[co["id"]] = sigs
        print(f"  {co['name']}: {len(sigs)} signals")

    total_signals = sum(len(v) for v in company_signal_map.values())
    print(f"\nTotal signals available: {total_signals}")

    # 2. Run generation for every company
    print("\n--- Running Hypothesis Engine across all companies ---")
    generation_results = []
    for co in companies:
        result = run_generation_for_company(co, company_signal_map[co["id"]])
        generation_results.append(result)
        time.sleep(2)  # brief pause between companies

    # 3. Pull all hypotheses now in DB
    print("\n--- Fetching all hypotheses from DB ---")
    all_hyps_raw = client.table("hypotheses").select("*, companies(name)").execute().data or []
    print(f"Total hypotheses in DB: {len(all_hyps_raw)}")

    # 4. Enrich with company name
    co_id_to_name = {co["id"]: co["name"] for co in companies}
    for h in all_hyps_raw:
        # Prefer the joined company name, fall back to lookup
        if h.get("companies") and isinstance(h["companies"], dict):
            h["company_name"] = h["companies"].get("name", "Unknown")
        else:
            h["company_name"] = co_id_to_name.get(h["company_id"], "Unknown")

    # 5. Grade every hypothesis
    print("\n--- Grading hypotheses (LLM, rate-limited) ---")
    graded = []
    for i, h in enumerate(all_hyps_raw):
        print(f"  [{i+1}/{len(all_hyps_raw)}] {h.get('title', '')[:60]}...")
        grade = grade_hypothesis(h, h["company_name"])
        if grade:
            h["grade"] = grade.get("grade", "F")
            h["specificity"] = grade.get("specificity", 0)
            h["novelty"] = grade.get("novelty", 0)
            h["actionability"] = grade.get("actionability", 0)
            h["grade_reasoning"] = grade.get("reasoning", "")
        else:
            h["grade"] = "UNGRADED"
            h["specificity"] = 0
            h["novelty"] = 0
            h["actionability"] = 0
            h["grade_reasoning"] = "Failed to parse"
        graded.append(h)
        time.sleep(1.2)  # avoid Groq 429

    # 6. Save raw graded export
    with open("sprint_d_hypotheses.json", "w", encoding="utf-8") as f:
        json.dump(graded, f, indent=2, default=str)
    print(f"\nExported {len(graded)} graded hypotheses -> sprint_d_hypotheses.json")

    # 7. Save CSV grading dataset (for manual review)
    csv_fields = ["id", "company_name", "type", "title", "confidence",
                  "status", "grade", "specificity", "novelty",
                  "actionability", "grade_reasoning", "created_at"]
    with open("sprint_d_grading_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(graded)
    print(f"Exported grading dataset -> sprint_d_grading_dataset.csv")

    # 8. Compute metrics
    print("\n" + "=" * 55)
    print("  HYPOTHESIS QUALITY REPORT v1")
    print("=" * 55)

    # Density
    hyps_by_company = defaultdict(list)
    for h in graded:
        hyps_by_company[h["company_name"]].append(h)

    print(f"\nHypothesis Density (per company):")
    for co_name, hyps in sorted(hyps_by_company.items(), key=lambda x: -len(x[1])):
        sig_count = len(company_signal_map.get(
            next((c["id"] for c in companies if c["name"] == co_name), ""), []
        ))
        density = len(hyps) / sig_count if sig_count > 0 else 0
        print(f"  {co_name}: {len(hyps)} hypotheses / {sig_count} signals "
              f"(density: {density:.3f})")

    # Grade distribution
    grade_counts = defaultdict(int)
    for h in graded:
        grade_counts[h["grade"]] += 1

    print(f"\nGrade Distribution (n={len(graded)}):")
    grade_order = ["A", "B", "C", "D", "F", "UNGRADED"]
    for g in grade_order:
        count = grade_counts[g]
        pct = (count / len(graded) * 100) if graded else 0
        bar = "█" * int(pct / 3)
        print(f"  {g}: {count:3d} ({pct:5.1f}%)  {bar}")

    # Average scores
    graded_only = [h for h in graded if h["grade"] != "UNGRADED"]
    if graded_only:
        avg_spec = sum(h["specificity"] for h in graded_only) / len(graded_only)
        avg_nov  = sum(h["novelty"] for h in graded_only) / len(graded_only)
        avg_act  = sum(h["actionability"] for h in graded_only) / len(graded_only)
        avg_conf = sum(float(h.get("confidence", 0)) for h in graded_only) / len(graded_only)
        print(f"\nAverage Scores (graded hypotheses only):")
        print(f"  Specificity:   {avg_spec:.2f} / 5")
        print(f"  Novelty:       {avg_nov:.2f} / 5")
        print(f"  Actionability: {avg_act:.2f} / 5")
        print(f"  Confidence:    {avg_conf:.2f}")

    # Duplicate rate (same title across companies)
    titles = [h.get("title", "") for h in graded]
    unique_titles = set(titles)
    dup_rate = 1 - (len(unique_titles) / len(titles)) if titles else 0
    print(f"\nDuplicate Rate: {dup_rate:.1%} ({len(titles) - len(unique_titles)} duplicates)")

    # Top A-grade hypotheses
    top = [h for h in graded if h["grade"] == "A"]
    if top:
        print(f"\nTop A-Grade Hypotheses ({len(top)} total):")
        for h in top[:5]:
            print(f"  [{h['company_name']}] {h['title'][:80]}")
        print(f"    -> {h['grade_reasoning']}")

    # Bottom F-grade hypotheses  
    noise = [h for h in graded if h["grade"] == "F"]
    if noise:
        print(f"\nF-Grade Noise Examples ({len(noise)} total):")
        for h in noise[:3]:
            print(f"  [{h['company_name']}] {h['title'][:80]}")
        print(f"    -> {h['grade_reasoning']}")

    print("\n" + "=" * 55)
    print("  Files:")
    print("    sprint_d_hypotheses.json     -- full export")
    print("    sprint_d_grading_dataset.csv -- for manual grading")
    print("=" * 55)


if __name__ == "__main__":
    main()
