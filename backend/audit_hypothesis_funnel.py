import sys
import os
import json
import logging
import time
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.analysis.hypothesis_engine import HypothesisEngine

logging.basicConfig(level=logging.INFO)

def audit_hypothesis_funnel():
    client = get_supabase_client()
    
    print("=== HYPOTHESIS FUNNEL AUDIT ===")
    
    for target in ["OpenAI", "Nvidia", "Anthropic", "Stripe"]:
        res = client.table("companies").select("id").eq("name", target).execute()
        if not res.data:
            print(f"Company {target} not found.")
            continue
        company_id = res.data[0]["id"]
        
        # Get all signals for this company
        sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
        signals = sig_res.data or []

        print(f"\n{'='*50}")
        print(f"  {target}")
        print(f"{'='*50}")
        
        if not signals:
            print("  No signals found.")
            continue
            
        # Force high importance so all signals are processed
        high_imp = []
        for s in signals:
            if str(s.get("signal_type")).upper() != "CORRELATION":
                s["importance"] = 8.0
                high_imp.append(s)
        high_imp.sort(key=lambda x: x.get("collected_at", ""), reverse=True)

        engine = HypothesisEngine()
        try:
            hypotheses = engine.generate_hypotheses(
                company_id=company_id,
                company_name=target,
                recent_signals=high_imp,
                trigger_reason="Funnel Audit"
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        m = engine.metrics

        # ── Full funnel printout (matches requested format) ─────────────────
        print()
        print(f"  signals_seen:                {m.get('signals_seen', 0)}")
        print(f"  signals_after_compression:   {m.get('signals_after_compression', 0)}")
        print(f"  tensions_extracted:          {m.get('tensions_extracted', 0)}")
        print(f"  tensions_discarded:          {m.get('tensions_discarded_no_evidence', 0)}  (< 2 signals per side)")

        tension_ex = m.get("tension_examples", [])
        if tension_ex:
            print(f"\n  Tension previews (first {len(tension_ex)}):")
            for i, t in enumerate(tension_ex, 1):
                print(f"    [{i}] A: {t.get('force_a', '(empty)')}")
                print(f"         B: {t.get('force_b', '(empty)')}")
                ev_a = t.get('evidence_a', [])
                ev_b = t.get('evidence_b', [])
                if ev_a:
                    print(f"         Evidence A: {ev_a[0][:80]}")
                if ev_b:
                    print(f"         Evidence B: {ev_b[0][:80]}")

        print(f"\n  candidate_actions_generated: {m.get('candidate_actions_generated', 0)}")

        # Show raw previews so we can distinguish real strategy from filler
        examples = m.get("candidate_examples", [])
        if examples:
            print(f"\n  Candidate previews (first {len(examples)}):")
            for i, ex in enumerate(examples, 1):
                print(f"    [{i}] ({ex.get('action', '?')}) {ex.get('preview', '(empty)')}")

        print(f"\n  validator_rejected:          {m.get('validator_rejected', 0)}")
        print(f"  dedup_rejected:              {m.get('dedup_rejected', 0)}")
        print(f"  final_created:               {m.get('final_created', 0)}")
        print(f"  final_updated:               {m.get('final_updated', 0)}")



        # ── Rejection breakdown ─────────────────────────────────────────────
        if m.get("validator_rejected", 0) > 0:
            print(f"\n  Rejection breakdown (CREATE):")
            print(f"    genericity_failures:     {m.get('genericity_failures', 0)}")
            print(f"    ceo_test_failures:       {m.get('ceo_test_failures', 0)}")
            print(f"    falsifiability_failures: {m.get('falsifiability_failures', 0)}")
        if m.get("dedup_rejected", 0) > 0:
            print(f"\n  Rejection breakdown (UPDATE regression):")
            print(f"    update_regression_failures: {m.get('update_regression_failures', 0)}")

        print(f"\n  quality_rejection_rate: {m.get('quality_rejection_rate', 0)}")
        print(f"  average_quality_score:  {m.get('average_quality_score', 0)}")
        # ────────────────────────────────────────────────────────────────────

        time.sleep(10)

if __name__ == "__main__":
    audit_hypothesis_funnel()
