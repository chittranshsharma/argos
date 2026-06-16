import sys
import os
import json
sys.path.append(os.getcwd())

from app.agents.executive_agent import ExecutiveAgent

class AuditExecutiveAgent(ExecutiveAgent):
    def __init__(self):
        super().__init__()
        self.audit_log = []

    def _extract_relevant_paragraphs(self, html: str, company_name: str) -> str:
        paras = super()._extract_relevant_paragraphs(html, company_name)
        self.current_paras = paras
        return paras

    def _extract_executive_events(self, text: str, company_name: str, url: str) -> list[dict]:
        events = super()._extract_executive_events(text, company_name, url)
        self.audit_log.append({
            "url": url,
            "paragraphs": self.current_paras if hasattr(self, 'current_paras') and self.current_paras else text,
            "llm_output": events
        })
        return events

agent = AuditExecutiveAgent()
print("Starting ExecutiveAgent noise audit on OpenAI, Anthropic, Scale AI, xAI...")

companies = ["OpenAI", "Anthropic", "Scale AI", "xAI"]
total_signals = 0

for comp in companies:
    print(f"\nScanning {comp}...")
    signals = agent.collect(company_name=comp, company_id=f"test-{comp.lower().replace(' ', '-')}")
    total_signals += len(signals)
    for s in signals:
        print(f"FOUND SIGNAL: {json.dumps(s, indent=2)}")

print(f"\n=======================")
print(f"TOTAL SIGNALS FOUND ACROSS ALL 4 COMPANIES: {total_signals}")
print(f"=======================\n")
