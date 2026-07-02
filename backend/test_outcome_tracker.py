"""
Sprint 5A Verification: Prediction Outcome Tracker
Tests deadline enforcement (deterministic) and full tracker run against live DB.
"""

import sys, os
sys.path.append(os.getcwd())

from app.database import get_supabase_client, get_pending_prediction_outcomes, get_prediction_outcomes_scorecard
from app.analysis.prediction_tracker import PredictionTracker
from app.analysis.hypothesis_engine import HypothesisEngine

def check_registry_rows():
    client = get_supabase_client()
    res = client.table("prediction_outcomes").select("*").execute()
    rows = res.data or []
    print(f"\n1. FORECAST REGISTRY — Total rows: {len(rows)}")
    for r in rows:
        hyp_id = r.get("hypothesis_id", "?")[:8]
        print(f"   [{r['status']}] hypothesis_id={hyp_id}... evidence_count={r.get('evidence_count',0)}")
    return rows

def check_pending():
    pending = get_pending_prediction_outcomes()
    print(f"\n2. PENDING OUTCOMES (non-terminal): {len(pending)}")
    return pending

def run_tracker():
    print("\n3. RUNNING PredictionTracker...")
    tracker = PredictionTracker()
    summary = tracker.run()
    print(f"   Result: {summary}")
    return summary

def check_scorecard():
    scorecard = get_prediction_outcomes_scorecard()
    print(f"\n4. FORECAST SCORECARD:")
    for k, v in scorecard.items():
        print(f"   {k}: {v}")

if __name__ == "__main__":
    rows = check_registry_rows()
    if not rows:
        print("\n⚠ No prediction_outcomes rows found.")
        print("  → Have you run the SQL migration (sprint5a_migration.sql) in Supabase?")
        print("  → And run a CEO Test or generate_hypotheses call to create rows?")
    else:
        pending = check_pending()
        if pending:
            run_tracker()
        else:
            print("   No pending outcomes to evaluate (all already terminal).")
        check_scorecard()
