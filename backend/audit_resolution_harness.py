"""
Argos — Resolution Audit Harness
Sprint 5A quality gate: compare tracker verdicts against human judgment.

Usage:
  Step 1 — Generate report:
    python backend/audit_resolution_harness.py --generate

  Step 2 — Human reviews the CSV (backend/resolution_audit_YYYYMMDD.csv)
    Fill in the `human_verdict` column with: AGREE / DISAGREE / PARTIAL
    Fill in `human_notes` with brief reasoning if you disagree.

  Step 3 — Score:
    python backend/audit_resolution_harness.py --score resolution_audit_YYYYMMDD.csv

  Output:
    Resolution Accuracy = X%
    Agreement breakdown
    Flagged cases for tracker prompt improvement
"""

import sys, os, csv, json, argparse
from datetime import datetime

sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client

AUDIT_DIR = "."


def generate_report():
    client = get_supabase_client()

    rows = client.table("prediction_outcomes").select(
        "id, hypothesis_id, status, confidence, verdict_payload, "
        "resolution_reason, evidence_signal_ids, evidence_count, created_at, updated_at"
    ).execute().data or []

    if not rows:
        print("No prediction_outcomes rows found. Generate hypotheses and run tracker first.")
        return

    # Enrich with hypothesis + signal details
    enriched = []
    for r in rows:
        hyp_res = client.table("hypotheses").select(
            "title, description, type, confidence, status, outcome, "
            "prediction_event, prediction_target, prediction_deadline_days, prediction_measurement"
        ).eq("id", r["hypothesis_id"]).execute()
        h = hyp_res.data[0] if hyp_res.data else {}

        vp = r.get("verdict_payload") or {}

        # Fetch signal details for matching signals
        signal_titles = vp.get("matching_signals", [])
        signal_details = []
        if r.get("evidence_signal_ids"):
            sigs = client.table("signals").select("id, title, content, signal_type, collected_at").in_(
                "id", r["evidence_signal_ids"][:5]
            ).execute()
            for s in (sigs.data or []):
                signal_details.append(f"{s.get('title','')} [{s.get('signal_type','')}]")

        enriched.append({
            # Identity
            "outcome_id": r["id"],
            "hypothesis_id": r["hypothesis_id"],
            # Hypothesis
            "hypothesis_title": h.get("title", ""),
            "hypothesis_type": h.get("type", ""),
            "hypothesis_description": h.get("description", "")[:200],
            # Prediction fields
            "prediction_event": h.get("prediction_event", ""),
            "prediction_target": h.get("prediction_target", ""),
            "prediction_deadline_days": h.get("prediction_deadline_days", ""),
            "prediction_measurement": h.get("prediction_measurement", ""),
            # Key quality flag: can CONFIRMED be trusted for this row?
            "prediction_structured": bool(h.get("prediction_event", "")),
            # Tracker verdict
            "tracker_status": r["status"],
            "tracker_confidence": r.get("confidence", ""),
            "tracker_verdict": vp.get("verdict", ""),
            "tracker_reasoning": vp.get("reasoning", ""),
            "cause_vs_outcome_check": vp.get("cause_vs_outcome_check", ""),
            "matching_signals": " | ".join(signal_titles[:5]),
            "evidence_signal_details": " | ".join(signal_details[:5]),
            "evidence_count": r.get("evidence_count", 0),
            # For human scoring (EXPIRED rows: verdict = N/A, deterministic)
            "human_verdict": "N/A" if r["status"] == "EXPIRED" else "",
            "human_notes": "Deterministic deadline expiry — no LLM" if r["status"] == "EXPIRED" else "",
            # Meta
            "updated_at": r.get("updated_at", ""),
        })

    # Write CSV
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"resolution_audit_{date_str}.csv"
    filepath = os.path.join(AUDIT_DIR, filename)

    fieldnames = list(enriched[0].keys()) if enriched else []
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)

    print(f"\nResolution Audit Report generated: {filepath}")
    print(f"Total outcomes: {len(enriched)}")
    print()
    print("Status breakdown:")
    from collections import Counter
    status_counts = Counter(r["tracker_status"] for r in enriched)
    for s, c in sorted(status_counts.items()):
        print(f"  {s}: {c}")
    print()
    print("Next steps:")
    print(f"  1. Open {filepath}")
    print("  2. Fill in 'human_verdict' column: AGREE / DISAGREE / PARTIAL")
    print("  3. Fill in 'human_notes' where you disagree")
    print(f"  4. Run: python backend/audit_resolution_harness.py --score {filename}")
    print()
    print(f"  Target: {len(enriched)} outcomes reviewed, Resolution Accuracy > 85%")
    print(f"  Current gap to 50-outcome threshold: {max(0, 50 - len(enriched))} more outcomes needed")

    return filename


def score_report(csv_file):
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    rows = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    scored = [r for r in rows if r.get("human_verdict", "").strip().upper() in ("AGREE", "DISAGREE", "PARTIAL")]
    if not scored:
        print("No human verdicts found. Fill in the 'human_verdict' column first.")
        print("Note: EXPIRED rows are pre-filled as N/A and excluded from scoring.")
        return

    # Exclude EXPIRED — deterministic, no classifier involved
    llm_scored = [r for r in scored if r.get("tracker_status", "") != "EXPIRED"]
    expired_count = sum(1 for r in rows if r.get("tracker_status", "") == "EXPIRED")

    if not llm_scored:
        print(f"All scored rows are EXPIRED (deterministic). Nothing to measure for LLM accuracy.")
        print(f"Generate more hypotheses and run the tracker to accumulate LLM classifications.")
        return

    total = len(llm_scored)
    agree = sum(1 for r in llm_scored if r["human_verdict"].strip().upper() == "AGREE")
    partial = sum(1 for r in llm_scored if r["human_verdict"].strip().upper() == "PARTIAL")
    disagree = sum(1 for r in llm_scored if r["human_verdict"].strip().upper() == "DISAGREE")

    # Resolution accuracy: AGREE=1, PARTIAL=0.5, DISAGREE=0 — excludes EXPIRED
    accuracy = (agree + 0.5 * partial) / total if total > 0 else 0

    # CONFIRMED precision (the critical metric)
    confirmed_rows = [r for r in llm_scored if r.get("tracker_status") == "CONFIRMED"]
    confirmed_agree = sum(1 for r in confirmed_rows if r["human_verdict"].strip().upper() == "AGREE")
    confirmed_precision = confirmed_agree / len(confirmed_rows) if confirmed_rows else None

    # CONTRADICTED precision
    contradicted_rows = [r for r in llm_scored if r.get("tracker_status") == "CONTRADICTED"]
    contradicted_agree = sum(1 for r in contradicted_rows if r["human_verdict"].strip().upper() == "AGREE")
    contradicted_precision = contradicted_agree / len(contradicted_rows) if contradicted_rows else None

    print("\n" + "=" * 60)
    print("RESOLUTION PRECISION REPORT")
    print("=" * 60)
    print(f"LLM-classified outcomes reviewed : {total}  (EXPIRED excluded: {expired_count})")
    print(f"  AGREE           : {agree}  ({agree/total*100:.0f}%)")
    print(f"  PARTIAL         : {partial}  ({partial/total*100:.0f}%)")
    print(f"  DISAGREE        : {disagree}  ({disagree/total*100:.0f}%)")
    print()
    print("── PRIMARY METRICS (gate for calibration) ──")
    if confirmed_precision is not None:
        gate_ok = confirmed_precision >= 0.85
        symbol = "✅" if gate_ok else "🚨"
        print(f"{symbol} CONFIRMED Precision : {confirmed_precision*100:.1f}%  ({confirmed_agree}/{len(confirmed_rows)}) ← must be >85% before calibration")
    else:
        print("   CONFIRMED Precision : No CONFIRMED outcomes scored yet")
    if contradicted_precision is not None:
        gate_ok = contradicted_precision >= 0.85
        symbol = "✅" if gate_ok else "🚨"
        print(f"{symbol} CONTRADICTED Precision: {contradicted_precision*100:.1f}%  ({contradicted_agree}/{len(contradicted_rows)})")
    else:
        print("   CONTRADICTED Precision: No CONTRADICTED outcomes scored yet")
    print()
    print("── SECONDARY METRIC ──")
    print(f"   Overall Resolution Accuracy: {accuracy*100:.1f}%  (AGREE+0.5×PARTIAL / total LLM rows)")
    print()

    # Calibration gate
    if confirmed_precision is not None and confirmed_precision >= 0.85:
        print("✅ CONFIRMED Precision gate passed — calibration is safe to build.")
    elif confirmed_precision is not None:
        print("🚨 CONFIRMED Precision below 85% — review tracker prompt before building calibration.")
    else:
        print("⏳ Not enough CONFIRMED outcomes yet. Generate more hypotheses and run tracker.")

    print()

    # List disagreements for analysis
    disagreements = [r for r in scored if r["human_verdict"].strip().upper() in ("DISAGREE", "PARTIAL")]
    if disagreements:
        print(f"Flagged cases ({len(disagreements)}) — review tracker prompt for these patterns:")
        print("-" * 60)
        for r in disagreements:
            print(f"[{r['human_verdict'].upper()}] {r['tracker_status']} | conf={r['tracker_confidence']}")
            print(f"  Hypothesis : {r['hypothesis_title'][:70]}")
            print(f"  Tracker    : {r['tracker_reasoning'][:120]}")
            print(f"  Human note : {r.get('human_notes','')}")
            print()

    # Status accuracy breakdown
    from collections import defaultdict
    by_status = defaultdict(lambda: {"agree": 0, "partial": 0, "disagree": 0})
    for r in scored:
        s = r["tracker_status"]
        v = r["human_verdict"].strip().upper()
        if v == "AGREE":
            by_status[s]["agree"] += 1
        elif v == "PARTIAL":
            by_status[s]["partial"] += 1
        else:
            by_status[s]["disagree"] += 1

    print("Accuracy by tracker status:")
    for status, counts in sorted(by_status.items()):
        total_s = sum(counts.values())
        acc_s = (counts["agree"] + 0.5 * counts["partial"]) / total_s
        print(f"  {status:<14} {acc_s*100:.0f}% ({total_s} samples)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolution Audit Harness")
    parser.add_argument("--generate", action="store_true", help="Generate audit CSV")
    parser.add_argument("--score", type=str, metavar="CSV_FILE", help="Score a completed audit CSV")
    args = parser.parse_args()

    if args.generate:
        generate_report()
    elif args.score:
        score_report(args.score)
    else:
        parser.print_help()
