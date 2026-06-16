import json
from app.analysis.hypothesis_engine import HypothesisQualityValidator
from collections import defaultdict
import time

benchmarks = [
    # OBVIOUS FAILURES (Expected: REJECT)
    {"id": 1, "type": "generic", "belief": "OpenAI is growing its revenue.", "strategic_tradeoff": "growth vs time", "prediction": "OpenAI will grow next quarter."},
    {"id": 2, "type": "generic", "belief": "OpenAI is expanding capabilities.", "strategic_tradeoff": "capabilities vs focus", "prediction": "OpenAI will release a feature."},
    {"id": 3, "type": "generic", "belief": "OpenAI faces competition.", "strategic_tradeoff": "competition vs market share", "prediction": "Competition will increase."},
    {"id": 4, "type": "generic", "belief": "OpenAI is hiring more engineers.", "strategic_tradeoff": "hiring vs cost", "prediction": "OpenAI will hire more people."},
    {"id": 5, "type": "generic", "belief": "OpenAI is improving its AI models.", "strategic_tradeoff": "quality vs speed", "prediction": "Models will get better."},
    {"id": 6, "type": "generic", "belief": "OpenAI is raising money.", "strategic_tradeoff": "equity vs capital", "prediction": "They will raise a round."},
    {"id": 7, "type": "generic", "belief": "OpenAI is opening a new office.", "strategic_tradeoff": "expansion vs cost", "prediction": "They will open an office."},
    {"id": 8, "type": "generic", "belief": "OpenAI is launching an app.", "strategic_tradeoff": "mobile vs desktop", "prediction": "They will launch an app."},
    {"id": 9, "type": "generic", "belief": "OpenAI is partnering with companies.", "strategic_tradeoff": "partnerships vs solo", "prediction": "More partnerships soon."},
    {"id": 10, "type": "generic", "belief": "OpenAI is facing lawsuits.", "strategic_tradeoff": "legal risk vs growth", "prediction": "More lawsuits will happen."},

    # BORDERLINE (Expected: MAYBE)
    {"id": 11, "type": "borderline", "belief": "OpenAI is using acquisitions to accelerate product breadth.", "strategic_tradeoff": "acquisition costs vs organic R&D", "prediction": "OpenAI will acquire an infrastructure startup within 6 months."},
    {"id": 12, "type": "borderline", "belief": "OpenAI is heavily subsidizing API costs to maintain developer mindshare.", "strategic_tradeoff": "API margin vs developer lock-in", "prediction": "OpenAI will drop API prices by 20% this year."},
    {"id": 13, "type": "borderline", "belief": "OpenAI is pivoting to enterprise sales to justify its valuation.", "strategic_tradeoff": "enterprise focus vs consumer focus", "prediction": "OpenAI will launch an enterprise tier."},
    {"id": 14, "type": "borderline", "belief": "OpenAI is building a moat through exclusive data partnerships.", "strategic_tradeoff": "partnership cost vs data advantage", "prediction": "OpenAI will sign 3 major media deals."},
    {"id": 15, "type": "borderline", "belief": "OpenAI is slowing down model releases to ensure safety compliance.", "strategic_tradeoff": "release speed vs safety", "prediction": "Next major model will be delayed by 3 months."},
    {"id": 16, "type": "borderline", "belief": "OpenAI is expanding internationally to avoid US regulatory bottlenecks.", "strategic_tradeoff": "international expansion cost vs US regulatory risk", "prediction": "OpenAI will open a European headquarters."},
    {"id": 17, "type": "borderline", "belief": "OpenAI is open-sourcing older models to commoditize competitors.", "strategic_tradeoff": "IP protection vs market commoditization", "prediction": "OpenAI will open-source a previous generation model."},
    {"id": 18, "type": "borderline", "belief": "OpenAI is vertically integrating hardware to reduce reliance on NVIDIA.", "strategic_tradeoff": "hardware R&D cost vs supplier dependence", "prediction": "OpenAI will announce a custom silicon project."},
    {"id": 19, "type": "borderline", "belief": "OpenAI is prioritizing consumer subscription revenue over API usage.", "strategic_tradeoff": "consumer MRR vs developer ecosystem", "prediction": "ChatGPT Plus will get exclusive features before API."},
    {"id": 20, "type": "borderline", "belief": "OpenAI is aggressively poaching talent to drain competitor R&D.", "strategic_tradeoff": "high compensation vs competitor velocity", "prediction": "OpenAI will hire a key executive from a rival."},

    # STRONG (Expected: PASS)
    {"id": 21, "type": "strong", "belief": "OpenAI appears willing to sacrifice margin to lock in enterprise distribution before model performance converges.", "strategic_tradeoff": "short-term profitability vs long-term distribution lock-in", "prediction": "OpenAI will announce aggressive flat-rate enterprise pricing that significantly undercuts Anthropic within 90 days."},
    {"id": 22, "type": "strong", "belief": "OpenAI is intentionally cannibalizing its own API partners by launching direct-to-consumer workflows.", "strategic_tradeoff": "ecosystem trust vs direct user relationship ownership", "prediction": "OpenAI will release a first-party tool that directly replaces a top-10 API partner's core product within 6 months."},
    {"id": 23, "type": "strong", "belief": "OpenAI is weaponizing open-source to commoditize the model layer while protecting its proprietary reasoning layer.", "strategic_tradeoff": "base model IP vs competitive moats", "prediction": "OpenAI will open-source its base GPT-4 model while keeping the reinforcement learning reasoning layer proprietary."},
    {"id": 24, "type": "strong", "belief": "OpenAI is treating legal fines as a calculated customer acquisition cost (CAC) rather than a deterrent.", "strategic_tradeoff": "regulatory compliance vs aggressive data ingestion", "prediction": "OpenAI will refuse to alter its scraping behavior in the EU, opting instead to pre-allocate funds for anticipated GDPR fines."},
    {"id": 25, "type": "strong", "belief": "OpenAI is silently shifting its core metric from 'intelligence capabilities' to 'inference efficiency'.", "strategic_tradeoff": "SOTA performance vs gross margins", "prediction": "The next major OpenAI release will boast cost-reductions rather than benchmark-breaking intelligence improvements."},
    {"id": 26, "type": "strong", "belief": "OpenAI is leveraging its Microsoft partnership solely to subsidize compute until it achieves hardware independence.", "strategic_tradeoff": "strategic autonomy vs immediate compute survival", "prediction": "OpenAI will announce a secondary, non-Microsoft cloud partnership or proprietary datacenter build out by Q4."},
    {"id": 27, "type": "strong", "belief": "OpenAI is abandoning the low-end consumer market to focus exclusively on highly regulated enterprise sectors (healthcare/finance).", "strategic_tradeoff": "consumer ubiquity vs high-margin compliance moats", "prediction": "OpenAI will launch a HIPAA/SOC2 dedicated environment with 10x premium pricing and sunset its free tier capabilities."},
    {"id": 28, "type": "strong", "belief": "OpenAI is purposely degrading the reliability of its legacy models to force enterprise migration to newer, higher-margin models.", "strategic_tradeoff": "legacy customer satisfaction vs forced upsell", "prediction": "Latency and error rates for GPT-3.5-turbo will measurably increase in the 30 days prior to its deprecation announcement."},
    {"id": 29, "type": "strong", "belief": "OpenAI is using consumer ChatGPT as a loss-leader data flywheel to train its enterprise B2B agents.", "strategic_tradeoff": "consumer compute costs vs proprietary human-feedback data", "prediction": "OpenAI will implement a mandatory data-sharing clause for free-tier users, refusing opt-outs to fuel its enterprise RLHF."},
    {"id": 30, "type": "strong", "belief": "OpenAI is positioning itself as a platform-tax layer, moving away from being an application provider.", "strategic_tradeoff": "first-party application revenue vs ecosystem tax", "prediction": "OpenAI will introduce a mandatory revenue-sharing agreement for top-tier GPT creators in its store."}
]

def run_audit():
    validator = HypothesisQualityValidator()
    results = []
    
    print("Starting Validator Audit...")
    for item in benchmarks:
        print(f"Evaluating [{item['type'].upper()}] - {item['belief'][:40]}...")
        
        # Rate limiting to avoid Groq 429
        time.sleep(1.0)
        
        res = validator.validate_create_action(item, "OpenAI")
        item_result = {
            "id": item["id"],
            "type": item["type"],
            "belief": item["belief"],
            "pass": res.get("pass", False),
            "scores": {
                "genericity": res.get("genericity_score", 0),
                "opposite": res.get("opposite_score", 0),
                "ceo": res.get("ceo_score", 0),
                "falsifiability": res.get("falsifiability_score", 0)
            },
            "reason": res.get("reason", "")
        }
        results.append(item_result)
        
    with open("validator_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("Audit complete! Results saved to validator_audit_results.json")

if __name__ == "__main__":
    run_audit()
