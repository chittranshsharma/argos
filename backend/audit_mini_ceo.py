import sys
import os
import logging
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.analysis.hypothesis_engine import HypothesisEngine
from unittest.mock import patch

logging.basicConfig(level=logging.DEBUG)

# We will patch save_analytics_snapshot to capture rejections
captured_rejections = []

def mock_save_snapshot(name, data):
    if name == "rejected_hypothesis_create":
        captured_rejections.append(data)

@patch('app.analysis.hypothesis_engine.save_analytics_snapshot', mock_save_snapshot)
def run_mini_ceo_test():
    client = get_supabase_client()
    companies = ["OpenAI", "Anthropic"]

    for target in companies:
        captured_rejections.clear()
        
        # 1. Fetch company ID
        res = client.table("companies").select("id").eq("name", target).execute()
        if not res.data:
            print(f"Company {target} not found.")
            continue
        company_id = res.data[0]["id"]

        # 2. Fetch signals
        sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
        signals = sig_res.data or []
        signals.sort(key=lambda x: x.get("collected_at", ""), reverse=True)

        # 3. Mark high importance
        high_imp = [s for s in signals if str(s.get("signal_type", "")).upper() != "CORRELATION"]
        for s in high_imp:
            s["importance"] = 8.0

        engine = HypothesisEngine()
        
        # 4. Generate hypotheses
        hypotheses = engine.generate_hypotheses(
            company_id=company_id,
            company_name=target,
            recent_signals=high_imp,
            trigger_reason="Mini CEO Test"
        )
        
        metrics = engine.metrics
        
        # 5. Print requested metrics
        print("="*60)
        print(f"Company: {target}")
        print(f"Hypotheses Created: {metrics.get('final_created', 0)}")
        print(f"Freshness Checked: {metrics.get('freshness_checked', 0)}")
        print(f"Freshness Rejected: {metrics.get('freshness_rejected', 0)}")
        print(f"Tensions Extracted: {metrics.get('tensions_extracted', 0)}")
        print(f"Tensions Overlap Checked: {metrics.get('tensions_overlap_checked', 0)}")
        print(f"Tensions Discarded (Low Overlap): {metrics.get('tensions_discarded_low_overlap', 0)}")
        print(f"Validator Rejected: {metrics.get('validator_rejected', 0)}")
        print("="*60)
        print()
        
        print("--- SURVIVING HYPOTHESES ---")
        if not hypotheses:
            print("None.")
        for h in hypotheses:
            print(f"TITLE: {h.get('title')}")
            # we don't have OBSERVATION, but we have description which contains Tradeoff, Prediction, Evidence
            print(f"DESCRIPTION (includes Interpretation/Prediction):\n{h.get('description')}")
            print("-" * 40)
            
        print("\n--- REJECTED HYPOTHESES ---")
        if not captured_rejections:
            print("None.")
        for r in captured_rejections:
            action = r.get("action", {})
            print(f"TITLE: {action.get('belief')}")
            
            scores = r.get("scores", {})
            reason = r.get("reason", "Unknown")
            rejection_type = "UNKNOWN"
            if "FRESHNESS_FAILURE" in reason:
                rejection_type = "FRESHNESS_FAILURE"
            elif "GENERICITY_FAILURE" in reason:
                rejection_type = "GENERICITY_FAILURE"
            elif "TIME_HORIZON_FAILURE" in reason:
                rejection_type = "TIME_HORIZON_FAILURE"
            elif "CEO_TEST_FAILURE" in reason:
                rejection_type = "CEO_TEST_FAILURE"
            elif "QUANTIFICATION_FAILURE" in reason:
                rejection_type = "QUANTIFICATION_FAILURE"
                
            print(f"REJECTION TYPE: {rejection_type}")
            print(f"REASON: {reason}")
            print("-" * 40)
        print("\n\n")

if __name__ == "__main__":
    run_mini_ceo_test()
