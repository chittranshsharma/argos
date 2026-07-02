import sys, os
sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()
from app.database import get_supabase_client
client = get_supabase_client()

res = client.table("prediction_outcomes").select(
    "status, confidence, resolution_reason, verdict_payload, hypothesis_id"
).execute()

print("=== PREDICTION OUTCOMES — FULL AUDIT TRAIL (V7) ===\n")
for r in (res.data or []):
    hyp = client.table("hypotheses").select(
        "title, prediction_event, prediction_target, prediction_deadline_days"
    ).eq("id", r["hypothesis_id"]).execute()
    h = hyp.data[0] if hyp.data else {}
    vp = r.get("verdict_payload") or {}
    
    print(f"STATUS     : {r['status']}  |  CONFIDENCE: {r.get('confidence')}")
    print(f"HYPOTHESIS : {h.get('title','?')[:80]}")
    print(f"EVENT      : {h.get('prediction_event','?')}")
    print(f"TARGET     : {h.get('prediction_target','?')}")
    print(f"DEADLINE   : {h.get('prediction_deadline_days','?')} days")
    print(f"VERDICT    : {vp.get('verdict','?')}")
    print(f"SIGNALS    : {vp.get('matching_signals',[])}")
    print(f"REASONING  : {vp.get('reasoning','?')}")
    print(f"RESOLUTION : {r.get('resolution_reason','')}")
    print("-" * 70)
