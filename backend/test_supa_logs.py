import sys
import os
sys.path.append(os.getcwd())

from app.database import get_supabase_client

client = get_supabase_client()
res = client.table('signals').select('id', count='exact').execute()
print(f"Total signals: {res.count}")

try:
    res = client.rpc('get_tables').execute()
    print("Tables via RPC:", res.data)
except Exception as e:
    pass

try:
    res = client.table('system_logs').select('*').limit(5).execute()
    print("system_logs:", res.data)
except Exception as e:
    pass

try:
    res = client.table('pipeline_logs').select('*').limit(5).execute()
    print("pipeline_logs:", res.data)
except Exception as e:
    pass

try:
    res = client.table('logs').select('*').limit(5).execute()
    print("logs:", res.data)
except Exception as e:
    pass
