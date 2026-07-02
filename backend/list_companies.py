"""
Sprint 5A Scale Run: Generate hypotheses for all companies, run tracker, report metrics.
"""
import sys, os
sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()

from app.database import get_all_companies, get_supabase_client

client = get_supabase_client()
companies = get_all_companies()
print(f"Total companies in watchlist: {len(companies)}")
for c in companies:
    sig = c.get("signals_count", 0) or 0
    score = c.get("intelligence_score", 0) or 0
    hyp_res = client.table("hypotheses").select("id", count="exact").eq("company_id", c["id"]).execute()
    hyp_count = hyp_res.count or 0
    print(f"  {c['name']:<30} signals={sig:<5} score={score:<6} hypotheses={hyp_count}")
