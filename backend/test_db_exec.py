import sys, os, json
sys.path.append(os.getcwd())
from app.database import get_supabase_client

client = get_supabase_client()
result = client.table("signals").select("*").eq("signal_type", "EXECUTIVE").order("collected_at", desc=True).limit(10).execute()

for s in result.data:
    print(json.dumps(s, indent=2))
