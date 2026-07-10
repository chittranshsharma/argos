"""
Script to manually trigger a single run of the Prediction Tracker to verify
snapshots are saved and the stale-signal guard fires.
"""
import sys, os, logging
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)
from dotenv import load_dotenv
load_dotenv()

from app.analysis.prediction_tracker import PredictionTracker
from app.database import get_supabase_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

tracker = PredictionTracker()
print("Running prediction tracker cycle...")
summary = tracker.run()
print("\nTracker Summary:")
print(summary)

print("\nVerifying snapshots in DB...")
client = get_supabase_client()
res = client.table("analytics_snapshots").select("*").eq("metric_type", "tracker_cycle").order("created_at", desc=True).limit(3).execute()
rows = res.data or []
if not rows:
    print("❌ No tracker_cycle snapshots found!")
else:
    print(f"✅ Found {len(rows)} recent tracker_cycle snapshots.")
    for r in rows:
        print(f"  [{r['created_at']}] {r['metrics_payload']}")
