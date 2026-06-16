import sys
import os
import json
import time
from datetime import datetime, timezone, timedelta

sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.agents.executive_agent import ExecutiveAgent
from app.agents.funding_agent import FundingAgent
from app.agents.jobs_agent import JobsAgent

COMPANIES = [
    {"name": "OpenAI", "id": "b18b45ea-271d-4076-a675-8b5e283921b7"},
    {"name": "Anthropic", "id": "4b68ce9d-6ebc-4734-93ff-41ff8e9b6bf7"},
    {"name": "Scale AI", "id": "cd0b6fa5-22d2-44f2-b883-820875c6543b"},
    {"name": "Databricks", "id": "e67e5ff8-2e38-4f1b-b4f3-2c1cfeb4b01e"},
    {"name": "Palantir", "id": "a93b45ea-271d-4076-a675-8b5e283921b8"} # Added random ID just for script
]

def force_scan():
    client = get_supabase_client()
    
    # Pre-fetch real IDs if they exist in DB
    try:
        res = client.table("companies").select("id, name, careers_url").execute()
        db_companies = {c["name"]: c for c in res.data}
    except Exception as e:
        print(f"Error fetching companies: {e}")
        db_companies = {}

    report_lines = []
    report_lines.append("# Argos Signal Quality Sprint")
    report_lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}\n")
    report_lines.append("For each signal, evaluate the following:")
    report_lines.append("- [ ] **Real?** Is this a genuine event or a hallucination/noise?")
    report_lines.append("- [ ] **Subtype correct?** Did the LLM classify the movement/event correctly?")
    report_lines.append("- [ ] **Payload complete?** Are all relevant fields extracted properly?")
    report_lines.append("- [ ] **Would analyst care?** Is this strategically relevant?")
    report_lines.append("- [ ] **Confidence justified?** Does the confidence score match the evidence?\n")
    report_lines.append("---\n")

    for target in COMPANIES:
        name = target["name"]
        db_info = db_companies.get(name)
        comp_id = db_info["id"] if db_info else target["id"]
        careers_url = db_info["careers_url"] if db_info and db_info.get("careers_url") else None
        
        print(f"==========================================")
        print(f"Scanning {name} ({comp_id})")
        print(f"==========================================")
        
        report_lines.append(f"## {name}")
        report_lines.append(f"ID: `{comp_id}`\n")
        
        agents = {
            "Funding": FundingAgent(),
            "Executive": ExecutiveAgent(),
        }
        if careers_url:
            agents["Hiring"] = JobsAgent()
            
        all_signals = []
        
        for agent_name, agent in agents.items():
            print(f"--> Running {agent_name} Agent...")
            try:
                if agent_name == "Hiring":
                    signals = agent.collect(careers_url=careers_url, company_name=name, company_id=comp_id)
                else:
                    signals = agent.collect(company_name=name, company_id=comp_id)
                print(f"    Found {len(signals)} signals.")
                all_signals.extend(signals)
            except Exception as e:
                print(f"    Failed: {e}")
                
        if not all_signals:
            report_lines.append("*No signals detected.*")
            report_lines.append("\n---\n")
            continue
            
        for s in all_signals:
            report_lines.append(f"### Signal: {s.get('title')}")
            report_lines.append(f"**Type:** `{s.get('signal_type')}` | **Subtype:** `{s.get('subtype')}` | **Agent:** `{s.get('agent')}`")
            report_lines.append(f"**URL:** {s.get('url', 'N/A')}")
            report_lines.append(f"**Confidence:** {s.get('payload', {}).get('confidence', 'N/A')}")
            report_lines.append("\n**Payload:**")
            report_lines.append("```json\n" + json.dumps(s.get("payload", {}), indent=2) + "\n```")
            report_lines.append("\n**Evaluation:**")
            report_lines.append("- [ ] Real?")
            report_lines.append("- [ ] Subtype correct?")
            report_lines.append("- [ ] Payload complete?")
            report_lines.append("- [ ] Would analyst care?")
            report_lines.append("- [ ] Confidence justified?")
            report_lines.append("\n**Notes:**\n\n---\n")

    with open("sprint_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\n✅ Scan complete. Generated sprint_report.md for manual validation.")

if __name__ == "__main__":
    force_scan()
