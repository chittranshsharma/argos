import sys
import os
import logging
sys.path.append(os.getcwd())

from app.agents.executive_agent import ExecutiveAgent

logging.basicConfig(level=logging.DEBUG)

agent = ExecutiveAgent()

print("Testing ExecutiveAgent on 'OpenAI'...")
signals = agent.collect(company_name="OpenAI", company_id="test-id")

print(f"Total deduplicated signals found: {len(signals)}")
if signals:
    for s in signals:
        print("\n---")
        print(f"Title: {s['title']}")
        print(f"Subtype: {s['subtype']}")
        print(f"Payload: {s['payload']}")
