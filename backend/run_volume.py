"""
Argos — Scale Volume Run
Generates hypotheses for ALL companies with sufficient signals,
then runs the prediction tracker, and reports population metrics.

This is not a test. This is reality-as-bottleneck mode.
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()

from app.database import get_all_companies, get_supabase_client, get_prediction_outcomes_scorecard
from app.analysis.hypothesis_engine import HypothesisEngine
from app.analysis.prediction_tracker import PredictionTracker

client = get_supabase_client()
companies = get_all_companies()

MIN_SIGNALS = 20  # skip companies with too few signals to form hypotheses

print("=" * 65)
print("ARGOS SCALE VOLUME RUN")
print("=" * 65)
print(f"Companies in watchlist: {len(companies)}")
eligible = [c for c in companies if (c.get("signals_count") or 0) >= MIN_SIGNALS]
print(f"Companies with {MIN_SIGNALS}+ signals (eligible): {len(eligible)}")
print()

# ─── Phase 1: Hypothesis Generation ─────────────────────────────
total_created = 0
total_updated = 0
company_results = []

for company in eligible:
    name = company["name"]
    cid  = company["id"]
    sig_count = company.get("signals_count", 0) or 0

    print(f"[GEN] {name:<30} (signals={sig_count})")

    try:
        signals = (
            client.table("signals")
            .select("*")
            .eq("company_id", cid)
            .order("collected_at", desc=True)
            .limit(50)
            .execute()
            .data or []
        )

        # Boost importance for non-correlation signals
        for s in signals:
            if str(s.get("signal_type", "")).upper() != "CORRELATION":
                s["importance"] = 8.0

        engine = HypothesisEngine()
        result = engine.generate_hypotheses(
            company_id=cid,
            company_name=name,
            recent_signals=signals,
            trigger_reason="Scale Volume Run"
        )

        m = engine.metrics
        created = m.get("final_created", 0)
        updated = m.get("final_updated", 0)
        rejected = m.get("quality_rejections", 0)
        tensions = m.get("tensions_extracted", 0)

        total_created += created
        total_updated += updated

        company_results.append({
            "name": name,
            "signals": sig_count,
            "tensions": tensions,
            "created": created,
            "updated": updated,
            "rejected": rejected,
        })

        print(f"       tensions={tensions} created={created} updated={updated} rejected={rejected}")

    except Exception as e:
        print(f"       ERROR: {e}")
        company_results.append({"name": name, "signals": sig_count, "error": str(e)})

    time.sleep(1)  # avoid hammering Groq rate limits between companies

print()
print(f"Phase 1 complete: {total_created} new hypotheses, {total_updated} updated")

# ─── Phase 2: Backfill any missing registry rows ─────────────────
print()
print("[BACKFILL] Ensuring all hypotheses have prediction_outcomes rows...")
from app.database import create_prediction_outcome

all_hyp = client.table("hypotheses").select("id, status").execute().data or []
existing = {r["hypothesis_id"] for r in client.table("prediction_outcomes").select("hypothesis_id").execute().data or []}
missing = [h for h in all_hyp if h["id"] not in existing]
for h in missing:
    create_prediction_outcome(h["id"])
print(f"  Backfilled {len(missing)} missing registry rows")

# ─── Phase 3: Run Prediction Tracker ─────────────────────────────
print()
print("[TRACKER] Running prediction outcome tracker on all pending outcomes...")
tracker = PredictionTracker()
tracker_summary = tracker.run()
print(f"  {tracker_summary}")

# ─── Phase 4: Population Metrics ─────────────────────────────────
print()
print("=" * 65)
print("POPULATION METRICS")
print("=" * 65)

# Hypothesis survival metrics
total_hyp = len(all_hyp)
hyp_res = client.table("hypotheses").select("status, type").execute().data or []
from collections import Counter
status_counts = Counter(h.get("status", "?") for h in hyp_res)
type_counts   = Counter(h.get("type", "?") for h in hyp_res)

print(f"Total hypotheses: {len(hyp_res)}")
print()
print("By status:")
for s, c in sorted(status_counts.items()):
    print(f"  {s:<20} {c}")
print()
print("By type:")
for t, c in sorted(type_counts.items()):
    print(f"  {t:<30} {c}")

# Prediction outcome distribution
print()
scorecard = get_prediction_outcomes_scorecard()
print("Forecast Registry:")
print(f"  Total tracked         : {scorecard.get('predictions_tracked', 0)}")
print(f"  UNRESOLVED            : {scorecard.get('predictions_unresolved', 0)}")
print(f"  SUPPORTED             : {scorecard.get('predictions_supported', 0)}")
print(f"  CONTRADICTED          : {scorecard.get('predictions_contradicted', 0)}")
print(f"  CONFIRMED             : {scorecard.get('predictions_confirmed', 0)}")
print(f"  INCORRECT             : {scorecard.get('predictions_incorrect', 0)}")
print(f"  EXPIRED               : {scorecard.get('predictions_expired', 0)}")
print(f"  Hit rate              : {scorecard.get('hit_rate', 'N/A')} {scorecard.get('hit_rate_note', '')}")

# Funnel metrics
total_tracked = scorecard.get("predictions_tracked", 0) or 1
pct = lambda x: f"{x/total_tracked*100:.0f}%" if total_tracked else "N/A"
print()
print("Outcome distribution (% of tracked):")
print(f"  Ever reached SUPPORTED    : {pct(scorecard.get('predictions_supported',0) + scorecard.get('predictions_confirmed',0))}")
print(f"  Confirmed                 : {pct(scorecard.get('predictions_confirmed',0))}")
print(f"  Contradicted              : {pct(scorecard.get('predictions_contradicted',0))}")
print(f"  Expired (deadline)        : {pct(scorecard.get('predictions_expired',0))}")
print(f"  Still pending             : {pct(scorecard.get('predictions_unresolved',0) + scorecard.get('predictions_supported',0) + scorecard.get('predictions_contradicted',0))}")

# Per-company generation summary
print()
print("Generation results per company:")
print(f"  {'Company':<30} {'signals':>7} {'tensions':>8} {'created':>8} {'updated':>8} {'rejected':>9}")
print("  " + "-" * 65)
for r in company_results:
    if "error" in r:
        print(f"  {r['name']:<30} ERROR: {r['error'][:40]}")
    else:
        print(f"  {r['name']:<30} {r.get('signals',0):>7} {r.get('tensions',0):>8} {r.get('created',0):>8} {r.get('updated',0):>8} {r.get('rejected',0):>9}")

print()
print("=" * 65)
print("Volume run complete.")
