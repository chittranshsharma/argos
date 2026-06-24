import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(override=True)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

COMPANIES = ["OpenAI", "Anthropic", "Stripe", "Nvidia", "Databricks"]

def run_audit():
    # Fetch company IDs
    res = client.table("companies").select("id, name").in_("name", COMPANIES).execute()
    companies = res.data or []
    
    audit_data = {}
    
    for comp in companies:
        c_name = comp["name"]
        c_id = comp["id"]
        
        # Fetch last 100 signals
        sig_res = client.table("signals").select("*").eq("company_id", c_id).order("collected_at", desc=True).limit(100).execute()
        signals = sig_res.data or []
        
        extracted = []
        for s in signals:
            raw = s.get("raw_data") or {}
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: raw = {}
                
            title = s.get("title") or raw.get("title", "Unknown Title")
            url = raw.get("url") or raw.get("link", "Unknown URL")
            agent = raw.get("agent", "Unknown Agent")
            
            extracted.append({
                "id": s.get("id"),
                "title": title,
                "agent": agent,
                "url": url
            })
            
        audit_data[c_name] = extracted
        print(f"Fetched {len(extracted)} signals for {c_name}")
        
    with open("signal_audit.json", "w") as f:
        json.dump(audit_data, f, indent=2)
        
if __name__ == "__main__":
    run_audit()
