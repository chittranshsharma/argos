import os
from app.database import get_supabase_client
client = get_supabase_client()
company_id = client.table("companies").select("id").eq("name", "Databricks").execute().data[0]["id"]
hyps = client.table("hypotheses").select("*").eq("company_id", company_id).execute().data
for h in hyps:
    print("- " + h["title"] + " (Conf: " + str(h["confidence"]) + ", Status: " + h["status"] + ")")
evals = client.table("hypothesis_evaluations").select("id", count="exact").in_("hypothesis_id", [h["id"] for h in hyps]).execute()
snaps = client.table("hypothesis_snapshots").select("id", count="exact").in_("hypothesis_id", [h["id"] for h in hyps]).execute()
print("Evals: " + str(evals.count) + ", Snaps: " + str(snaps.count))
