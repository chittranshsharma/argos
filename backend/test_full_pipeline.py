import sys
import os
import logging
sys.path.append(os.getcwd())

from app.database import get_company_by_id
from app.pipeline.nodes import collect_signals_node, filter_new_signals_node

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("app.pipeline.validator")
logger.setLevel(logging.ERROR)

company = get_company_by_id('ab4d1d45-dc2a-441f-8d85-c65e1d14cb99')

state = {
    "company_data": company,
    "company_name": company["name"],
    "company_id": company["id"]
}

print("Running collect_signals_node...")
state = collect_signals_node(state)
print(f"Total raw signals collected: {len(state.get('raw_signals', []))}")

print("Running filter_new_signals_node...")
res = filter_new_signals_node(state)
new_signals = res.get("new_signals", [])

print(f"Total new signals: {len(new_signals)}")
