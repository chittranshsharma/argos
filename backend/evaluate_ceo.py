import requests
import json

API_BASE = "http://localhost:8001"
COMPANIES = ["OpenAI", "Anthropic", "Stripe", "Nvidia", "Databricks"]

def fetch_data():
    try:
        res = requests.get(f"{API_BASE}/companies")
        all_comps = res.json().get("companies", [])
        
        target_comps = [c for c in all_comps if c["name"] in COMPANIES]
        
        md = ["# CEO Test V2 - Hypothesis Review\n"]
        for comp in target_comps:
            name = comp["name"]
            c_id = comp["id"]
            
            hyp_res = requests.get(f"{API_BASE}/companies/{c_id}/hypotheses")
            hyps = hyp_res.json().get("hypotheses", [])
            
            md.append(f"## {name} ({len(hyps)} hypotheses)\n")
            for h in hyps:
                md.append(f"### {h.get('title')}")
                md.append(f"{h.get('description')}")
                md.append("**Evidence:**")
                for e in h.get("evidence", []):
                    md.append(f"- {e}")
                md.append("\n---\n")
            
        with open("ceo_evaluation_v2.md", "w") as f:
            f.write("\n".join(md))
            
        print(f"Successfully exported data for {len(target_comps)} companies.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_data()
