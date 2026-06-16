import sys
import os
import json
from datetime import datetime, timezone

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
    {"name": "Palantir", "id": "a93b45ea-271d-4076-a675-8b5e283921b8"}
]

def run_reliability_validation():
    client = get_supabase_client()
    
    # Pre-fetch careers_urls if they exist
    try:
        res = client.table("companies").select("id, name, careers_url").execute()
        db_companies = {c["name"]: c for c in res.data}
    except Exception as e:
        print(f"Error fetching companies: {e}")
        db_companies = {}

    report_lines = []
    report_lines.append("# Sprint 1.5: Reliability Validation Report")
    report_lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}\n")
    report_lines.append("## Evaluation Criteria")
    report_lines.append("For each signal, evaluate:")
    report_lines.append("1. **Validity:** Is this factually true based on the URL?")
    report_lines.append("2. **Severity (if invalid):** Minor (meta error), Moderate (wrong subtype), Critical (hallucinated fact/person)")
    report_lines.append("3. **Confidence Accuracy:** Is the confidence calibration appropriate?")
    report_lines.append("4. **Queue Hit:** Did it correctly route to auto_approved or pending?\n")
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
            payload = s.get("payload", {})
            reasoning = payload.get("confidence_reasoning", {})
            review_status = payload.get("review_status", s.get("review_status", "unknown"))
            confidence = payload.get("confidence", s.get("confidence", 0.0))
            
            report_lines.append(f"### Signal: {s.get('title')}")
            report_lines.append(f"**Type:** `{s.get('signal_type')}` | **Subtype:** `{s.get('subtype')}` | **Agent:** `{s.get('agent')}`")
            report_lines.append(f"**URL:** {s.get('url', 'N/A')}")
            report_lines.append(f"**Confidence:** {confidence}")
            report_lines.append(f"**Review Status:** `{review_status}`")
            report_lines.append("\n**Confidence Reasoning:**")
            report_lines.append("```json\n" + json.dumps(reasoning, indent=2) + "\n```")
            report_lines.append("\n**Payload:**")
            report_lines.append("```json\n" + json.dumps(payload, indent=2) + "\n```")
            report_lines.append("\n**Evaluation:**")
            report_lines.append("- [ ] **Valid?** (Yes/No)")
            report_lines.append("- [ ] **Severity if Invalid:** (Minor/Moderate/Critical)")
            report_lines.append("- [ ] **Confidence calibrated?** (Yes/No)")
            report_lines.append("- [ ] **Routing correct?** (Yes/No)")
            report_lines.append("\n**Notes:**\n\n---\n")

    with open("reliability_review.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\n✅ Scan complete. Generated reliability_review.md for rigorous manual validation.")

if __name__ == "__main__":
    run_reliability_validation()
