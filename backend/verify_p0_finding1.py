"""
P0 Verification: Finding #1
Are prediction_event, prediction_deadline_days, prediction_target,
and prediction_measurement actually persisted in the hypotheses table?

Run from project root:
    python backend/verify_p0_finding1.py
"""
import sys, os
# Works whether run from project root or backend/ directly
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)
from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client

client = get_supabase_client()

print("\n" + "="*70)
print("  P0 VERIFICATION: Structured Prediction Fields in hypotheses table")
print("="*70)

# 1. Count totals and nulls across all four prediction fields
res = client.table("hypotheses").select(
    "id, status, prediction_event, prediction_deadline_days, "
    "prediction_target, prediction_measurement, title, created_at, company_id"
).execute()
rows = res.data or []

total = len(rows)
if total == 0:
    print("No hypotheses found in DB. Nothing to verify.")
    sys.exit(0)

event_set       = sum(1 for r in rows if r.get("prediction_event") and str(r["prediction_event"]).strip())
deadline_set    = sum(1 for r in rows if r.get("prediction_deadline_days") is not None)
target_set      = sum(1 for r in rows if r.get("prediction_target") and str(r["prediction_target"]).strip())
measurement_set = sum(1 for r in rows if r.get("prediction_measurement") and str(r["prediction_measurement"]).strip())

print(f"\nTotal hypotheses: {total}")
print(f"\n{'Field':<30} {'Populated':>10} {'NULL/Empty':>12} {'% Populated':>12}")
print("-"*66)
for label, count in [
    ("prediction_event",           event_set),
    ("prediction_deadline_days",   deadline_set),
    ("prediction_target",          target_set),
    ("prediction_measurement",     measurement_set),
]:
    null_count = total - count
    pct = count / total * 100
    flag = " <- CRITICAL" if pct < 50 else (" <- OK" if pct > 80 else " <- PARTIAL")
    print(f"  {label:<28} {count:>10} {null_count:>12} {pct:>11.1f}%{flag}")

# 2. Verdict
print("\n" + "-"*66)
any_critical = min(event_set, deadline_set) < total * 0.5

if any_critical:
    print("VERDICT: FINDING #1 IS REAL")
    print()
    print("  prediction_event and/or prediction_deadline_days are NULL")
    print("  for most hypotheses. This means:")
    print("    - _is_expired() returns False for most -> no expiry")
    print("    - CONFIRMED blocked for unstructured hyps -> inflated UNRESOLVED")
    print("    - Calibration data is partially invalid")
    print()
    print("  ACTION: Fix hyp_record in hypothesis_engine.py before any other work.")
elif event_set < total * 0.8:
    print("VERDICT: FINDING #1 IS PARTIALLY REAL (some rows missing fields)")
else:
    print("VERDICT: FINDING #1 IS A FALSE POSITIVE")
    print("  Structured prediction fields are populated.")

# 3. Sample rows for inspection
print("\n" + "-"*66)
print("SAMPLE ROWS (first 10):")
print(f"  {'ID':>8}  {'status':<14} {'event':>5} {'deadline':>9} {'company':<20} {'created'}")
print("  " + "-"*75)
for r in rows[:10]:
    has_event    = "Y" if r.get("prediction_event") else "N"
    has_deadline = str(r.get("prediction_deadline_days", "NULL"))
    print(f"  {r['id'][:8]}  {r.get('status','?'):<14} {has_event:>5} {has_deadline:>9} "
          f"{str(r.get('title','?'))[:30]:<30} {str(r.get('created_at',''))[:10]}")

# 4. Tracker compatibility
print("\n" + "-"*66)
expirable = [r for r in rows
             if r.get("prediction_deadline_days") is not None
             and r.get("created_at")]
print(f"Rows tracker can expire (deadline + created_at set): {len(expirable)}/{total}")
if len(expirable) < total * 0.5:
    print("  FAIL: Most hypotheses cannot expire. Tracker leaves them UNRESOLVED forever.")
else:
    print("  PASS: Majority of hypotheses have deadline data the tracker can use.")

# 5. Active hypothesis breakdown
active = [r for r in rows if r.get("status") == "ACTIVE"]
active_structured = [r for r in active if r.get("prediction_event") and r.get("prediction_deadline_days")]
print(f"\nActive hypotheses:            {len(active)}")
print(f"Active + fully structured:    {len(active_structured)}")
if active and len(active_structured) < len(active) * 0.5:
    print("  FAIL: Majority of ACTIVE forecasts lack structured fields.")

print("\n" + "="*70 + "\n")
