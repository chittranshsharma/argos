"""
Sprint 5A End-to-End Validation
Runs all 7 checks sequentially and reports results.
"""
import sys, os
sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client, get_all_companies, get_prediction_outcomes_scorecard

client = get_supabase_client()

# ── V1: Column exists ─────────────────────────────────────────
print("\n=== V1: calibrated_confidence column ===")
try:
    client.table("hypotheses").select("calibrated_confidence").limit(1).execute()
    print("  PASS — column queryable")
except Exception as e:
    print(f"  FAIL — {e}")

# ── V2: Table exists and row count before ─────────────────────
print("\n=== V2: prediction_outcomes table ===")
res = client.table("prediction_outcomes").select("id", count="exact").execute()
before_count = res.count or 0
print(f"  Rows before hypothesis generation: {before_count}")

# ── V3: Generate one hypothesis (OpenAI) ─────────────────────
print("\n=== V3: Generating hypotheses for OpenAI ===")
companies = get_all_companies()
target = next((c for c in companies if "openai" in c.get("name","").lower()), companies[0] if companies else None)
if not target:
    print("  SKIP — no companies found")
else:
    print(f"  Target: {target['name']}")
    from app.analysis.hypothesis_engine import HypothesisEngine
    engine = HypothesisEngine()
    recent_signals = client.table("signals").select("*").eq("company_id", target["id"]).order("collected_at", desc=True).limit(30).execute().data or []
    result = engine.generate_hypotheses(
        company_id=target["id"],
        company_name=target["name"],
        recent_signals=recent_signals,
        trigger_reason="Sprint 5A Validation"
    )
    print(f"  Hypotheses created/updated: {len(result)}")

    # ── V4: Check registry rows created ──────────────────────
    print("\n=== V4: prediction_outcomes rows after generation ===")
    res2 = client.table("prediction_outcomes").select("id, status, hypothesis_id", count="exact").execute()
    after_count = res2.count or 0
    print(f"  Rows after: {after_count} (was {before_count})")
    new_rows = after_count - before_count
    if new_rows == len(result):
        print(f"  PASS — {new_rows} new registry rows match {len(result)} hypotheses")
    elif new_rows > 0:
        print(f"  PARTIAL — {new_rows} rows created, {len(result)} hypotheses")
    else:
        print(f"  FAIL — No new registry rows created")

    for r in (res2.data or [])[:5]:
        print(f"    [{r['status']}] hyp={r['hypothesis_id'][:8]}...")

# ── V5: Expiry test (deterministic, no LLM) ──────────────────
print("\n=== V5: Hard Deadline / Expiry Test ===")
from datetime import datetime, timezone, timedelta
from app.analysis.prediction_tracker import PredictionTracker

# Find a non-expired pending outcome
pending_res = client.table("prediction_outcomes").select("*, hypotheses(*)").not_.in_("status", ["CONFIRMED", "INCORRECT", "EXPIRED"]).limit(1).execute()
if pending_res.data:
    test_outcome = pending_res.data[0]
    test_hyp_id = test_outcome["hypothesis_id"]
    
    # Force the hypothesis created_at to 30 days ago and deadline to 1 day
    old_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    client.table("hypotheses").update({
        "created_at": old_date,
        "prediction_deadline_days": 1
    }).eq("id", test_hyp_id).execute()
    print(f"  Set hypothesis {test_hyp_id[:8]}... created_at=30 days ago, deadline=1 day")
    
    # Run tracker — should expire this
    tracker = PredictionTracker()
    summary = tracker.run()
    print(f"  Tracker summary: {summary}")
    
    # Check the specific outcome
    check = client.table("prediction_outcomes").select("status, resolution_reason").eq("hypothesis_id", test_hyp_id).execute()
    if check.data:
        status = check.data[0]["status"]
        if status == "EXPIRED":
            print(f"  PASS — status is EXPIRED (no LLM call)")
        else:
            print(f"  FAIL — status is {status}, expected EXPIRED")
    else:
        print("  FAIL — no outcome row found")
else:
    print("  SKIP — no pending outcomes to test (run after V3)")

# ── V6: Scorecard endpoint check ─────────────────────────────
print("\n=== V6: Scorecard forecast metrics ===")
scorecard = get_prediction_outcomes_scorecard()
required_keys = ["predictions_tracked", "predictions_confirmed", "predictions_expired", "hit_rate"]
for k in required_keys:
    val = scorecard.get(k, "MISSING")
    status = "PASS" if k in scorecard else "FAIL"
    print(f"  {status} {k}: {val}")
print(f"  Full scorecard: {scorecard}")

print("\n=== Validation Complete ===")
