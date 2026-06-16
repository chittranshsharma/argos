import sys
import os
import logging
sys.path.append(os.getcwd())

from app.database import get_all_companies
from app.agents.executive_agent import ExecutiveAgent

logging.basicConfig(level=logging.INFO)

companies = get_all_companies()
agent = ExecutiveAgent()

all_signals = []

for c in companies[:3]: # test top 3 companies
    print(f"Collecting for {c['name']}...")
    signals = agent.collect(company_name=c['name'], company_id=c['id'])
    if signals:
        all_signals.extend(signals)

import json
print(f"Total extracted signals across companies: {len(all_signals)}")
for i, s in enumerate(all_signals[:10]):
    print(f"\n[Signal {i+1}]")
    print(json.dumps(s, indent=2))
