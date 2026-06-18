import sys
import os
import logging
import time
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.analysis.hypothesis_engine import HypothesisEngine
from app.analysis.signal_compressor import compress_signals

logging.basicConfig(level=logging.WARNING)  # Suppress INFO noise

def run():
    client = get_supabase_client()
    target = "OpenAI"

    res = client.table("companies").select("id").eq("name", target).execute()
    company_id = res.data[0]["id"]

    sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
    signals = sig_res.data or []

    # Sort newest first (ordering fix from D.4.1)
    signals.sort(key=lambda x: x.get("collected_at", ""), reverse=True)

    # Mark all non-correlation signals as high importance (as production would)
    high_imp = [s for s in signals if str(s.get("signal_type", "")).upper() != "CORRELATION"]
    for s in high_imp:
        s["importance"] = 8.0

    # Show what the compressor will produce
    compressed = compress_signals(high_imp[:50])
    context_chars = sum(len(s["summary"]) for s in compressed)
    token_estimate = context_chars // 4

    print(f"=== Sprint D.5A: Signal Compressor Test ===")
    print(f"Company: {target}")
    print(f"Total signals in DB: {len(signals)}")
    print(f"High-importance signals: {len(high_imp)}")
    print(f"Signals sent to HypothesisEngine: {min(50, len(high_imp))}")
    print(f"Compressed context ~tokens: {token_estimate}")
    print()
    print("Sample compressed signals (first 3):")
    for s in compressed[:3]:
        print(f"  [{s['signal_type']}] {s['title'][:60]}")
        print(f"    summary: {s['summary'][:120]}")
    print()

    engine = HypothesisEngine()
    try:
        hypotheses = engine.generate_hypotheses(
            company_id=company_id,
            company_name=target,
            recent_signals=high_imp,
            trigger_reason="Sprint D.5A Compressor Test"
        )
    except Exception as e:
        print(f"Error: {e}")
        return

    metrics = getattr(engine, "metrics", {})

    print("=== Funnel Results ===")
    print(f"Candidate Actions Proposed by LLM: {metrics.get('evaluations_created', 0) + metrics.get('hypotheses_created', 0)}")
    print(f"  - Genericity Failures:       {metrics.get('genericity_failures', 0)}")
    print(f"  - CEO Test Failures:          {metrics.get('ceo_test_failures', 0)}")
    print(f"  - Falsifiability Failures:    {metrics.get('falsifiability_failures', 0)}")
    print(f"  - Dedup Rejections:           {metrics.get('hypotheses_deduplicated', 0)}")
    print(f"Successful Creations:           {metrics.get('hypotheses_created', 0)}")
    print(f"Final Hypotheses This Run:      {len(hypotheses)}")

if __name__ == "__main__":
    run()
