import json
import logging
from dotenv import load_dotenv

from app.database import get_all_companies, get_supabase_client, get_signals
from app.analysis.hypothesis_engine import HypothesisEngine

load_dotenv(override=True)
logging.basicConfig(level=logging.WARNING)

TARGETS = ["OpenAI", "Anthropic"]

def run():
    companies = get_all_companies()
    target_comps = [c for c in companies if c["name"] in TARGETS]
    
    engine = HypothesisEngine()
    
    for c in target_comps:
        print(f"\n{'='*80}")
        print(f"  TENSION FUNNEL AUDIT: {c['name']}")
        print(f"{'='*80}")
        
        # Fetch signals
        signals = get_signals(c["id"], limit=50)
        print(f"[{c['name']}] Found {len(signals)} signals in DB.")
        
        if not signals:
            print("No signals found, skipping.")
            continue
            
        # Run engine
        engine.generate_hypotheses(c["id"], c["name"], signals, "Tension Audit")
        
        # Print metrics
        m = engine.metrics
        
        print(f"\n--- FUNNEL METRICS ---")
        print(f"Signals Seen:                 {m.get('signals_seen', 0)}")
        print(f"Signals After Compression:    {m.get('signals_after_compression', 0)}")
        print(f"Tensions Extracted:           {m.get('tensions_extracted', 0)}")
        print(f"Tensions Discarded (No Ev):   {m.get('tensions_discarded_no_evidence', 0)}")
        print(f"Candidate Actions Generated:  {m.get('candidate_actions_generated', 0)}")
        print(f"Forced CREATE Conversions:    {m.get('forced_create_conversions', 0)}")
        print(f"Update Missing Hyp ID Drops:  {m.get('update_missing_hypothesis_id', 0)}")
        print(f"Avg Proper Nouns per Candidate:{m.get('proper_noun_count_avg', 0.0)}")
        print(f"Validator Rejected:           {m.get('validator_rejected', 0)}")
        print(f"Dedup Rejected:               {m.get('dedup_rejected', 0)}")
        print(f"Final Created:                {m.get('final_created', 0)}")
        print(f"Final Updated:                {m.get('final_updated', 0)}")
        
        print("\n--- ACTUAL TENSIONS EXTRACTED ---")
        if m.get("tension_examples"):
            for i, t in enumerate(m["tension_examples"], 1):
                print(f"\nTension {i}:")
                print(f"  Force A: {t.get('force_a', '')}")
                print(f"  Force B: {t.get('force_b', '')}")
                print(f"  Evidence A: {t.get('evidence_a', [])}")
                print(f"  Evidence B: {t.get('evidence_b', [])}")
        else:
            print("  (None extracted)")
            
        print("\n--- ACTUAL CANDIDATES GENERATED ---")
        if m.get("candidate_examples"):
            for i, cand in enumerate(m["candidate_examples"], 1):
                print(f"\nCandidate {i}:")
                print(f"  Action:  {cand.get('action', '')}")
                print(f"  Preview: {cand.get('preview', '')}")
        else:
            print("  (None generated)")

if __name__ == "__main__":
    run()
