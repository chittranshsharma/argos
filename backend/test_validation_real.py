import sys
import os
import logging
sys.path.append(os.getcwd())

from app.database import get_company_by_id
from app.pipeline.nodes import collect_signals_node
from app.pipeline.validator import SignalValidator

logging.basicConfig(level=logging.WARNING)

company = get_company_by_id('ab4d1d45-dc2a-441f-8d85-c65e1d14cb99')
state = {
    "company_data": company,
    "company_name": company["name"],
    "company_id": company["id"]
}

print("Collecting signals...")
state = collect_signals_node(state)
raw_signals = state.get("raw_signals", [])
print(f"Total raw: {len(raw_signals)}")

validator = SignalValidator()
valid = []
invalid = []

for sig in raw_signals:
    agent_name = sig.get("agent", "Unknown")
    res = validator.validate_and_format(sig, agent_name)
    if res:
        valid.append(sig)
    else:
        invalid.append(sig)

print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")
if invalid:
    print("Invalid samples:")
    for inv in invalid[:5]:
        print(inv.get("title", "No Title"), "->", inv.get("url", "No URL"))
