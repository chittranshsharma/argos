from app.database import get_supabase_client
import json

client = get_supabase_client()
data = client.table('analytics_snapshots').select('*').eq('metric_type', 'rejected_hypothesis_create').execute().data

print(f"Found {len(data)} rejected CREATE hypotheses.")
for row in data:
    payload = row.get("payload_json", {})
    action = payload.get("action", {})
    scores = payload.get("scores", {})
    print(f"\n{'='*50}")
    print(f"REJECTED BELIEF: {action.get('belief')}")
    print(f"{'='*50}")
    print(f"SCORES: Genericity: {scores.get('genericity_score')}, CEO: {scores.get('ceo_score')}, Falsifiability: {scores.get('falsifiability_score')}, Opposite: {scores.get('opposite_score')}")
    print(f"REASON: {payload.get('reason')}")
