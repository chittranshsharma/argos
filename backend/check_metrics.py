from app.database import get_supabase_client

client = get_supabase_client()
res = client.table("analytics_snapshots").select("*").eq("metric_type", "correlation_metrics").order("timestamp", desc=True).limit(5).execute()

print("--- Correlation Metrics ---")
for r in res.data:
    print(r)
