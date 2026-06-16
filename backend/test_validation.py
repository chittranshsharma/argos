import sys
import os
import logging
sys.path.append(os.getcwd())

from app.agents.news_agent import NewsAgent
from app.agents.hackernews_agent import HackerNewsAgent
from app.pipeline.validator import SignalValidator

logging.basicConfig(level=logging.INFO)

news_agent = NewsAgent()
hn_agent = HackerNewsAgent()

company_name = "OpenAI"
company_id = "test-id"

print("Collecting news...")
news_signals = news_agent.collect(keywords=["OpenAI"], company_name=company_name, company_id=company_id)
print("Collecting HN...")
hn_signals = hn_agent.collect(company_name=company_name, company_id=company_id)

all_signals = news_signals + hn_signals
print(f"Total raw: {len(all_signals)}")

validator = SignalValidator()
valid_count = 0
invalid_count = 0

for sig in all_signals:
    res = validator.validate_and_format(sig, "test_agent")
    if res:
        valid_count += 1
    else:
        invalid_count += 1

print(f"Valid: {valid_count}, Invalid: {invalid_count}")
