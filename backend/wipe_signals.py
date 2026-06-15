import sys
from app.database import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
client = get_supabase_client()
res = client.table('signals').delete().eq('company_name', 'OpenAI').execute()
print(f"Deleted {len(res.data)} signals for OpenAI")
