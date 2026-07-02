import sys
import os
import logging
import json
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.analysis.hypothesis_engine import HypothesisEngine
from app.analysis.signal_compressor import compress_signals

logging.basicConfig(level=logging.WARNING)

def run_a1_audit():
    client = get_supabase_client()
    company = "Anthropic"
    
    # 1. Fetch company ID
    res = client.table("companies").select("id").eq("name", company).execute()
    if not res.data:
        print(f"Company {company} not found.")
        return
    company_id = res.data[0]["id"]

    # 2. Fetch all signals
    sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
    signals = sig_res.data or []
    
    # Filter to only the A1 signals
    keywords = ["tag", "mythos", "fable", "export", "korea", "government", "restriction", "trump", "jailbreak"]
    
    a1_signals = []
    for s in signals:
        text = (s.get("title", "") + " " + s.get("summary", "")).lower()
        if any(k in text for k in keywords):
            s["importance"] = 8.0 # force high importance
            a1_signals.append(s)
            
    a1_signals.sort(key=lambda x: x.get("collected_at", ""), reverse=True)
    
    print("=== FOCUSED A1 AUDIT ===")
    print(f"Total A1 Signals Selected: {len(a1_signals)}")
    for s in a1_signals:
        print(f"- {s['title']}")
        
    print("\n--- COMPRESSION ---")
    compressed = compress_signals(a1_signals[:20])
    for c in compressed:
        print(f"[{c['signal_type']}] {c['title']}: {c['summary']}")
        
    print("\n--- TENSION EXTRACTION & HYPOTHESIS GENERATION ---")
    
    engine = HypothesisEngine()
    
    # Capture rejected actions using a mock
    from unittest.mock import patch
    rejected = []
    def mock_save(*args):
        if args[0] == "rejected_hypothesis_create":
            rejected.append(args[1])
            
    with patch('app.analysis.hypothesis_engine.save_analytics_snapshot', mock_save):
        engine.generate_hypotheses(company_id, company, a1_signals[:20], "A1 Audit")
        
    print("\n--- RESULTS ---")
    
    print("\n=== REJECTED CANDIDATES ===")
    for r in rejected:
        action = r.get("action", {})
        print(f"BELIEF (Title): {action.get('belief')}")
        print(f"TRADEOFF: {action.get('strategic_tradeoff')}")
        print(f"RAW ACTION JSON:\n{json.dumps(action, indent=2)}")
        print(f"REASON: {r.get('reason')}")
        print("-" * 40)
        
    print("\n=== SURVIVING CANDIDATES ===")
    # Surviving hypotheses are saved in the DB, so we can fetch them or just assume if not rejected they passed
    res_hyps = client.table("hypotheses").select("*").eq("company_id", company_id).execute()
    hyps = res_hyps.data or []
    for h in hyps:
        print(f"BELIEF (Title): {h.get('title')}")
        print(f"DESCRIPTION: {h.get('description')}")
        print("-" * 40)

if __name__ == "__main__":
    run_a1_audit()
