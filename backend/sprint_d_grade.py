"""
Sprint D - Grade existing hypotheses and produce quality report.
Skips generation (already done). Grades all hypotheses in DB.
"""
import json
import csv
import re
import time
from collections import defaultdict
from app.database import get_supabase_client
from app.llm import get_groq_llm, llm_invoke

client = get_supabase_client()
llm = get_groq_llm()

GRADE_PROMPT = """You are a strategic intelligence analyst grading a generated hypothesis.

Company: {company_name}
Belief: {title}
Description: {description}
Confidence: {confidence}

Grade using this rubric (choose ONE letter only):
A = Decision-changing insight -- a CEO could act on this immediately, bold and specific claim
B = Useful synthesis -- combines signals in a non-obvious way, directionally useful
C = Accurate summary -- correctly describes company behaviour but adds no new framing
D = Generic observation -- true of most companies in the sector, not specific here
F = Noise -- vague, contradicted by evidence, or strategically empty

Score 1-5:
- specificity: how specific to THIS company vs any company in the sector
- novelty: how non-obvious given the raw signals
- actionability: could an analyst act on this today

Return ONLY valid JSON:
{{
  "grade": "A",
  "specificity": 3,
  "novelty": 3,
  "actionability": 3,
  "reasoning": "one sentence explanation"
}}"""


def grade_hypothesis(h: dict, company_name: str) -> dict:
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
    return {}


def main():
    companies = client.table("companies").select("id, name").execute().data or []
    co_id_to_name = {c["id"]: c["name"] for c in companies}

    all_hyps = client.table("hypotheses").select("*").execute().data or []
    print(f"Total hypotheses to grade: {len(all_hyps)}")

    graded = []
    for i, h in enumerate(all_hyps):
        h["company_name"] = co_id_to_name.get(h["company_id"], "Unknown")
        g = grade_hypothesis(h, h["company_name"])
        h["grade"] = g.get("grade", "UNGRADED")
        h["specificity"] = g.get("specificity", 0)
        h["novelty"] = g.get("novelty", 0)
        h["actionability"] = g.get("actionability", 0)
        h["grade_reasoning"] = g.get("reasoning", "")
        graded.append(h)
        print(f"  [{i+1}/{len(all_hyps)}] {h['company_name']} | {h['grade']} | {h.get('title','')[:55]}")
        time.sleep(1.2)

    # Save JSON
    with open("sprint_d_hypotheses.json", "w", encoding="utf-8") as f:
        json.dump(graded, f, indent=2, default=str)
    print(f"\nSaved sprint_d_hypotheses.json ({len(graded)} records)")

    # Save CSV
    csv_fields = ["id", "company_name", "type", "title", "confidence",
                  "status", "grade", "specificity", "novelty", "actionability",
                  "grade_reasoning", "created_at"]
    with open("sprint_d_grading_dataset.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(graded)
    print("Saved sprint_d_grading_dataset.csv")

    # Report
    print("\n" + "=" * 55)
    print("  HYPOTHESIS QUALITY REPORT v1")
    print("=" * 55)

    # Grade distribution
    grade_counts = defaultdict(int)
    for h in graded:
        grade_counts[h["grade"]] += 1

    print(f"\nGrade Distribution (n={len(graded)}):")
    for g in ["A", "B", "C", "D", "F", "UNGRADED"]:
        n = grade_counts[g]
        pct = (n / len(graded) * 100) if graded else 0
        bar = "#" * int(pct / 4)
        print(f"  {g}: {n:3d}  ({pct:5.1f}%)  {bar}")

    # Per-company count
    hyps_by_co = defaultdict(list)
    for h in graded:
        hyps_by_co[h["company_name"]].append(h)

    print(f"\nHypotheses per company:")
    for co, hyps in sorted(hyps_by_co.items(), key=lambda x: -len(x[1])):
        grades = "".join(h["grade"] for h in hyps)
        print(f"  {co:<25} {len(hyps):3d}  [{grades}]")

    # Average scores
    graded_only = [h for h in graded if h["grade"] not in ("UNGRADED",)]
    if graded_only:
        avg_spec = sum(h["specificity"] for h in graded_only) / len(graded_only)
        avg_nov  = sum(h["novelty"] for h in graded_only) / len(graded_only)
        avg_act  = sum(h["actionability"] for h in graded_only) / len(graded_only)
        avg_conf = sum(float(h.get("confidence", 0)) for h in graded_only) / len(graded_only)
        print(f"\nAverage Scores:")
        print(f"  Specificity:   {avg_spec:.2f} / 5")
        print(f"  Novelty:       {avg_nov:.2f} / 5")
        print(f"  Actionability: {avg_act:.2f} / 5")
        print(f"  DB Confidence: {avg_conf:.2f}")

    # Density
    total_signals = sum(
        len(client.table("signals").select("id").eq("company_id", c["id"]).execute().data or [])
        for c in companies
    )
    density = len(graded) / len(companies) if companies else 0
    sig_density = len(graded) / total_signals if total_signals else 0
    print(f"\nHypothesis Density:")
    print(f"  Total companies:  {len(companies)}")
    print(f"  Total signals:    {total_signals}")
    print(f"  Total hypotheses: {len(graded)}")
    print(f"  Hyps/company:     {density:.1f}")
    print(f"  Hyps/signal:      {sig_density:.4f}")

    # Top examples
    top = [h for h in graded if h["grade"] == "A"]
    if top:
        print(f"\nA-Grade Hypotheses ({len(top)}):")
        for h in top:
            print(f"  [{h['company_name']}]")
            print(f"  {h.get('title','')[:90]}")
            print(f"  Reasoning: {h['grade_reasoning']}")

    noise = [h for h in graded if h["grade"] == "F"]
    if noise:
        print(f"\nF-Grade (Noise) Examples ({len(noise)}):")
        for h in noise[:3]:
            print(f"  [{h['company_name']}] {h.get('title','')[:80]}")
            print(f"  Reasoning: {h['grade_reasoning']}")

    print("\n" + "=" * 55)
    print("  Done. Deliverables:")
    print("    sprint_d_hypotheses.json     -- full graded export")
    print("    sprint_d_grading_dataset.csv -- manual review CSV")
    print("=" * 55)


if __name__ == "__main__":
    main()
