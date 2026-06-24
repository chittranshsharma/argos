import json
import logging
from dotenv import load_dotenv

from app.database import get_all_companies, get_supabase_client
from app.pipeline.graph import monitoring_graph

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)

TARGETS = ["OpenAI", "Anthropic", "Stripe", "Nvidia", "Databricks"]

def clear_old_signals_and_hyps(company_id):
    # Delete existing signals and hypotheses
    get_supabase_client().table("signals").delete().eq("company_id", company_id).execute()
    get_supabase_client().table("hypotheses").delete().eq("company_id", company_id).execute()
    print(f"Cleared old signals and hypotheses for {company_id}")

def run():
    companies = get_all_companies()
    target_comps = [c for c in companies if c["name"] in TARGETS]
    
    for c in target_comps:
        print(f"\n--- Processing {c['name']} ---")
        clear_old_signals_and_hyps(c["id"])
        
        # We also need to mock or ensure the website is in the company data
        # Normally company_data has it, but if it doesn't we provide it.
        website = c.get("website", "")
        if not website:
            domains = {
                "OpenAI": "openai.com",
                "Anthropic": "anthropic.com",
                "Nvidia": "nvidia.com",
                "Stripe": "stripe.com",
                "Databricks": "databricks.com"
            }
            website = f"https://{domains[c['name']]}"
            c["website"] = website
            
        # Update news_keywords in DB just in case they are completely generic
        # We will use the company name as the safe keyword.
        # AutoDiscoverer update handles future onboarding, but for these 5 we can just force the safe keyword.
        c["news_keywords"] = [c["name"]]
        
        initial_state = {
            "company_id": c["id"],
            "company_name": c["name"],
            "company_data": c,
            "raw_signals": [],
            "new_signals": [],
            "filtered_signals": [],
            "hypotheses": []
        }
        
        # Run pipeline
        try:
            result = monitoring_graph.invoke(initial_state)
            print(f"Successfully generated {len(result['hypotheses'])} hypotheses for {c['name']}.")
        except Exception as e:
            print(f"Pipeline failed for {c['name']}: {e}")

if __name__ == "__main__":
    run()
