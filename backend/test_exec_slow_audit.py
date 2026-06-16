import sys, os, json, time, re
sys.path.append(os.getcwd())
from app.agents.executive_agent import ExecutiveAgent

class SlowAuditExecutiveAgent(ExecutiveAgent):
    def __init__(self):
        super().__init__()
        self.audit_log = []

    def _extract_executive_events(self, text: str, company_name: str, url: str) -> list[dict]:
        # Only process if we haven't got 3 yet
        if len([a for a in self.audit_log if a.get("llm_output")]) >= 3:
            return []
            
        print(f"Sleeping 20s to respect Groq TPM limit before processing {url}...")
        time.sleep(20)
        
        events = super()._extract_executive_events(text, company_name, url)
        
        if events:
            self.audit_log.append({
                "url": url,
                "paragraphs": text,
                "llm_output": events
            })
            
        return events

agent = SlowAuditExecutiveAgent()
print("Starting Slow Audit on OpenAI & Anthropic...")

signals = []
for comp in ["OpenAI", "Anthropic", "Scale AI", "xAI"]:
    if len([a for a in agent.audit_log if a.get("llm_output")]) >= 3:
        break
    print(f"Fetching articles for {comp}...")
    new_sigs = agent.collect(company_name=comp, company_id=f"test-{comp.lower()}")
    if new_sigs:
        signals.extend(new_sigs)

print("\n\n" + "="*50)
print("AUDIT RESULTS")
print("="*50)

printed = 0
for audit in agent.audit_log:
    if not audit["llm_output"]: continue
    
    print(f"\n```json id=\"{printed+1}\"")
    output_obj = {
        "article": audit["url"],
        "paragraphs": audit["paragraphs"],
        "llm_output": audit["llm_output"]
    }
    
    final_sig = None
    for s in signals:
        if s["url"] == audit["url"]:
            final_sig = s.copy()
            break
            
    if final_sig:
        output_obj["final_signal"] = final_sig.copy()
        
        db_record = final_sig.copy()
        raw_data = db_record.get("raw_data", {})
        for key in ["confidence", "subtype", "source_id", "agent", "extraction_model", "occurred_at", "payload"]:
            if key in db_record:
                raw_data[key] = db_record.pop(key)
        db_record["raw_data"] = raw_data
        
        output_obj["db_record"] = db_record
        
    print(json.dumps(output_obj, indent=2))
    print("```\n")
    printed += 1
    if printed >= 3:
        break
