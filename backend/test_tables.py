import sys
import os
import json
sys.path.append(os.getcwd())

from app.database import get_supabase_client
client = get_supabase_client()

import httpx
url = str(client.supabase_url) + "/rest/v1/"
headers = {"apikey": client.supabase_key, "Authorization": f"Bearer {client.supabase_key}"}

try:
    r = httpx.get(url, headers=headers)
    schema = r.json()
    tables = [k.replace('/', '') for k in schema.get('paths', {}).keys()]
    print("Tables:", [t for t in set(tables) if '{' not in t and 'rpc' not in t])
except Exception as e:
    print("Error:", e)
