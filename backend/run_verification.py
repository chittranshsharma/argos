import json
import logging
from app.agents.news_agent import NewsAgent
from dotenv import load_dotenv

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)

companies = [
    {"name": "OpenAI", "website": "https://openai.com", "keywords": ["OpenAI", "ChatGPT", "GPT-4o", "Sam Altman"]},
    {"name": "Anthropic", "website": "https://www.anthropic.com", "keywords": ["Anthropic", "Claude", "Dario Amodei"]},
    {"name": "Nvidia", "website": "https://www.nvidia.com", "keywords": ["Nvidia", "Jensen Huang", "GeForce"]},
    {"name": "Stripe", "website": "https://stripe.com", "keywords": ["Stripe", "Patrick Collison"]},
    {"name": "Databricks", "website": "https://databricks.com", "keywords": ["Databricks", "Ali Ghodsi", "Apache Spark"]}
]

agent = NewsAgent()
all_signals = {}

for c in companies:
    print(f"Collecting for {c['name']}...")
    signals = agent.collect(keywords=c["keywords"], company_name=c["name"], company_id="test", website=c["website"])
    
    extracted = []
    for s in signals:
        extracted.append({
            "id": "test",
            "title": s["title"],
            "agent": s["agent"],
            "url": s["url"]
        })
    all_signals[c["name"]] = extracted

with open("signal_audit_v2.json", "w") as f:
    json.dump(all_signals, f, indent=2)

print("Saved to signal_audit_v2.json")
