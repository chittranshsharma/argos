import sys
import os
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.main import run_monitoring_for_company
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

client = get_supabase_client()
res = client.table('companies').select('*').ilike('name', 'OpenAI').execute()
if res.data:
    company = res.data[0]
    print(f"Running monitoring for {company['name']}...")
    run_monitoring_for_company(company)
else:
    print("Company OpenAI not found.")
