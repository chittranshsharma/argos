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

    # BORDERLINE (Expected: UNLABELED / DIAGNOSTIC)
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
    {"id": 31, "type": "borderline", "belief": "OpenAI is limiting support for legacy models to force upgrades.", "strategic_tradeoff": "legacy support vs upgrade revenue", "prediction": "OpenAI will deprecate a legacy API endpoint within 6 months."},
    {"id": 32, "type": "borderline", "belief": "OpenAI is trying to dominate the agentic ecosystem.", "strategic_tradeoff": "platform vs tools", "prediction": "OpenAI will launch an agent marketplace."},
    {"id": 33, "type": "borderline", "belief": "OpenAI is prioritizing security over capabilities.", "strategic_tradeoff": "security vs features", "prediction": "OpenAI will hire a new Chief Information Security Officer."},
    {"id": 34, "type": "borderline", "belief": "OpenAI is trying to lock in major cloud providers.", "strategic_tradeoff": "exclusivity vs multi-cloud", "prediction": "OpenAI will sign an exclusive compute deal with another cloud provider."},
    {"id": 35, "type": "borderline", "belief": "OpenAI is shifting to a freemium enterprise model.", "strategic_tradeoff": "freemium vs direct sales", "prediction": "OpenAI will offer a restricted enterprise tier for free."},
    {"id": 36, "type": "borderline", "belief": "OpenAI is aggressively targeting the defense sector.", "strategic_tradeoff": "defense contracts vs public image", "prediction": "OpenAI will announce a partnership with the DoD."},
    {"id": 37, "type": "borderline", "belief": "OpenAI is struggling with compute limits.", "strategic_tradeoff": "compute constraints vs velocity", "prediction": "OpenAI will delay their next training run."},
    {"id": 38, "type": "borderline", "belief": "OpenAI is increasing focus on edge computing.", "strategic_tradeoff": "edge vs cloud", "prediction": "OpenAI will release a lightweight model optimized for mobile devices."},
    {"id": 39, "type": "borderline", "belief": "OpenAI is consolidating its product lines.", "strategic_tradeoff": "consolidation vs breadth", "prediction": "OpenAI will merge DALL-E into the base GPT interface permanently."},
    {"id": 40, "type": "borderline", "belief": "OpenAI is reducing its reliance on RLHF.", "strategic_tradeoff": "RLHF vs unsupervised", "prediction": "OpenAI will publish a paper on unsupervised reasoning."},

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
    {"id": 30, "type": "strong", "belief": "OpenAI is positioning itself as a platform-tax layer, moving away from being an application provider.", "strategic_tradeoff": "first-party application revenue vs ecosystem tax", "prediction": "OpenAI will introduce a mandatory revenue-sharing agreement for top-tier GPT creators in its store."},
    {"id": 41, "type": "strong", "belief": "OpenAI is pivoting its monetization strategy away from compute usage to value-based pricing.", "strategic_tradeoff": "predictable token revenue vs outcome-based value capture", "prediction": "OpenAI will introduce flat-fee pricing based on business outcomes rather than token usage for its enterprise tier."},
    {"id": 42, "type": "strong", "belief": "OpenAI is silently deprecating its plugins ecosystem in favor of native agent workflows.", "strategic_tradeoff": "developer ecosystem trust vs integrated product experience", "prediction": "OpenAI will announce the sunsetting of the ChatGPT plugins store in favor of GPTs within the next quarter."},
    {"id": 43, "type": "strong", "belief": "OpenAI is intentionally capping open-source contributions to starve competitors of talent.", "strategic_tradeoff": "academic reputation vs proprietary talent retention", "prediction": "OpenAI will restrict its researchers from publishing open-source model weights."},
    {"id": 44, "type": "strong", "belief": "OpenAI is leveraging regulatory capture to build a moat against smaller competitors.", "strategic_tradeoff": "open innovation ethos vs regulatory moat", "prediction": "OpenAI will actively lobby for mandatory compute thresholds for AI safety evaluations."},
    {"id": 45, "type": "strong", "belief": "OpenAI is subsidizing its consumer app with enterprise revenue to build an unbreakable data flywheel.", "strategic_tradeoff": "enterprise margins vs consumer data dominance", "prediction": "OpenAI will offer unlimited consumer access to its most advanced model while raising enterprise API prices."},
    {"id": 46, "type": "strong", "belief": "OpenAI is shifting from a generalized AI provider to a specialized vertical workflow engine.", "strategic_tradeoff": "horizontal platform vs vertical dominance", "prediction": "OpenAI will release three industry-specific models (healthcare, legal, finance) by the end of the year."},
    {"id": 47, "type": "strong", "belief": "OpenAI is abandoning hardware independence efforts due to capital constraints.", "strategic_tradeoff": "hardware autonomy vs capital efficiency", "prediction": "OpenAI will quietly cancel its custom silicon program and sign a multi-year exclusive extension with NVIDIA."},
    {"id": 48, "type": "strong", "belief": "OpenAI is weaponizing its partnership network to block Anthropic's enterprise adoption.", "strategic_tradeoff": "open ecosystem vs vendor lock-in", "prediction": "OpenAI will require exclusivity agreements for its top 100 enterprise partners, forbidding the use of Anthropic models."},
    {"id": 49, "type": "strong", "belief": "OpenAI is intentionally delaying its next flagship model to maximize revenue from current generation models.", "strategic_tradeoff": "innovation velocity vs immediate revenue maximization", "prediction": "OpenAI will push the release of its next flagship model past Q4 despite it being ready for deployment."},
    {"id": 50, "type": "strong", "belief": "OpenAI is fundamentally changing its corporate structure to attract traditional private equity.", "strategic_tradeoff": "non-profit mission vs unlimited capital access", "prediction": "OpenAI will announce a full transition to a standard for-profit entity, eliminating its capped-profit structure."},

    # ADVERSARIAL GENERIC (Expected: REJECT)
    {"id": 51, "type": "adversarial_generic", "belief": "OpenAI is accelerating ecosystem growth.", "strategic_tradeoff": "ecosystem vs isolated product", "prediction": "OpenAI will expand its ecosystem to support long-term growth."},
    {"id": 52, "type": "adversarial_generic", "belief": "OpenAI is strengthening its core business.", "strategic_tradeoff": "core focus vs peripheral projects", "prediction": "OpenAI will continue strengthening its competitive position through strategic investments."},
    {"id": 53, "type": "adversarial_generic", "belief": "OpenAI is optimizing its talent pool.", "strategic_tradeoff": "talent density vs headcount", "prediction": "OpenAI will attract world-class talent to drive future product innovations."},
    {"id": 54, "type": "adversarial_generic", "belief": "OpenAI is enhancing market penetration.", "strategic_tradeoff": "penetration vs margin", "prediction": "OpenAI will pursue synergistic partnerships that enhance market reach."},
    {"id": 55, "type": "adversarial_generic", "belief": "OpenAI is doubling down on artificial general intelligence.", "strategic_tradeoff": "AGI research vs current features", "prediction": "OpenAI will aggressively invest resources to achieve breakthroughs in AGI."},
    {"id": 56, "type": "adversarial_generic", "belief": "OpenAI is prioritizing customer satisfaction.", "strategic_tradeoff": "CSAT vs innovation", "prediction": "OpenAI will implement broad initiatives to improve the overall customer experience."},
    {"id": 57, "type": "adversarial_generic", "belief": "OpenAI is scaling its infrastructure.", "strategic_tradeoff": "infrastructure cost vs uptime", "prediction": "OpenAI will scale its underlying architecture to meet growing global demand."},
    {"id": 58, "type": "adversarial_generic", "belief": "OpenAI is diversifying its revenue streams.", "strategic_tradeoff": "diversification vs focus", "prediction": "OpenAI will explore new monetization avenues to ensure long-term sustainability."},
    {"id": 59, "type": "adversarial_generic", "belief": "OpenAI is maintaining its technological lead.", "strategic_tradeoff": "R&D vs sales", "prediction": "OpenAI will introduce next-generation improvements to maintain its market dominance."},
    {"id": 60, "type": "adversarial_generic", "belief": "OpenAI is deepening enterprise engagement.", "strategic_tradeoff": "enterprise vs SMB", "prediction": "OpenAI will deepen relationships with key enterprise clients to drive retention."},

    # ADVERSARIAL NON-ACTIONABLE (Expected: REJECT)
    {"id": 61, "type": "adversarial_non_actionable", "belief": "OpenAI is pivoting to a platform-first approach.", "strategic_tradeoff": "platform vs app", "prediction": "OpenAI will transition into becoming the foundational AI layer for the modern internet."},
    {"id": 62, "type": "adversarial_non_actionable", "belief": "OpenAI is decentralizing AI safety research.", "strategic_tradeoff": "open vs closed safety", "prediction": "OpenAI will foster a collaborative global environment for AI alignment."},
    {"id": 63, "type": "adversarial_non_actionable", "belief": "OpenAI is preparing to out-compete Google.", "strategic_tradeoff": "search vs generative AI", "prediction": "OpenAI will deploy strategies that significantly disrupt established search paradigms."},
    {"id": 64, "type": "adversarial_non_actionable", "belief": "OpenAI is shifting focus to multi-modal interactions.", "strategic_tradeoff": "multi-modal vs text-only", "prediction": "OpenAI will seamlessly integrate vision, text, and audio into a unified cognitive framework."},
    {"id": 65, "type": "adversarial_non_actionable", "belief": "OpenAI is aiming for maximum market capitalization.", "strategic_tradeoff": "valuation vs immediate profit", "prediction": "OpenAI will orchestrate a paradigm shift in how corporate valuations are assessed in the AI sector."},
    {"id": 66, "type": "adversarial_non_actionable", "belief": "OpenAI is reducing systemic risk.", "strategic_tradeoff": "safety vs deployment speed", "prediction": "OpenAI will proactively mitigate existential risks associated with advanced machine learning systems."},
    {"id": 67, "type": "adversarial_non_actionable", "belief": "OpenAI is democratizing artificial intelligence.", "strategic_tradeoff": "accessibility vs exclusivity", "prediction": "OpenAI will ensure its powerful technologies are universally accessible across all socio-economic strata."},
    {"id": 68, "type": "adversarial_non_actionable", "belief": "OpenAI is capturing the developer mindshare.", "strategic_tradeoff": "developer focus vs end-user", "prediction": "OpenAI will empower developers worldwide with unparalleled building blocks."},
    {"id": 69, "type": "adversarial_non_actionable", "belief": "OpenAI is creating an impenetrable moat.", "strategic_tradeoff": "moat building vs feature release", "prediction": "OpenAI will leverage its unparalleled data flywheel to become an unstoppable force in the AI industry."},
    {"id": 70, "type": "adversarial_non_actionable", "belief": "OpenAI is streamlining internal operations.", "strategic_tradeoff": "efficiency vs rapid growth", "prediction": "OpenAI will achieve unprecedented operational efficiency through AI-driven automation."},

    # ADVERSARIAL STRONG (Expected: PASS)
    {"id": 71, "type": "strong", "belief": "OpenAI is aggressively targeting the healthcare sector.", "strategic_tradeoff": "healthcare compliance cost vs vertical lock-in", "prediction": "OpenAI will acquire an FDA-compliant healthcare data startup within 90 days."},
    {"id": 72, "type": "strong", "belief": "OpenAI is cannibalizing its consumer subscriptions.", "strategic_tradeoff": "ChatGPT Plus margin vs Anthropic disruption", "prediction": "OpenAI will drop the price of ChatGPT Plus to $10/month to undercut Anthropic Pro."},
    {"id": 73, "type": "strong", "belief": "OpenAI is attempting to dominate mobile AI.", "strategic_tradeoff": "Android parity vs Apple ecosystem dominance", "prediction": "OpenAI will announce a definitive hardware partnership with Apple to replace Siri."},
    {"id": 74, "type": "strong", "belief": "OpenAI is shifting its compute strategy.", "strategic_tradeoff": "US datacenter reliance vs global compute diversification", "prediction": "OpenAI will announce a multi-billion dollar datacenter build in the Middle East."},
    {"id": 75, "type": "strong", "belief": "OpenAI is facing internal safety backlash.", "strategic_tradeoff": "revenue growth vs employee retention", "prediction": "OpenAI will publicly launch a dedicated 'Alignment First' product tier following employee pressure."},
    {"id": 76, "type": "strong", "belief": "OpenAI is trying to lock in European markets.", "strategic_tradeoff": "EU expansion cost vs regulatory mitigation", "prediction": "OpenAI will open a physical AI research center in Paris."},
    {"id": 77, "type": "strong", "belief": "OpenAI is pushing for widespread enterprise adoption.", "strategic_tradeoff": "SMB scale vs enterprise high-touch", "prediction": "OpenAI will introduce a mandatory minimum $100k/year contract for its custom model training service."},
    {"id": 78, "type": "strong", "belief": "OpenAI is addressing its copyright lawsuits aggressively.", "strategic_tradeoff": "licensing costs vs continuous legal battles", "prediction": "OpenAI will sign a sweeping licensing agreement with the New York Times."},
    {"id": 79, "type": "strong", "belief": "OpenAI is abandoning its non-profit roots entirely.", "strategic_tradeoff": "mission perception vs capital acquisition", "prediction": "OpenAI will officially dissolve its non-profit board structure by the end of the year."},
    {"id": 80, "type": "strong", "belief": "OpenAI is focusing on edge computing.", "strategic_tradeoff": "cloud recurring revenue vs edge ubiquity", "prediction": "OpenAI will release a 2B parameter open-weight model optimized strictly for on-device inference."}
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
        
    # Metrics Calculation
    generic_total = 0
    generic_accepted = 0
    
    strong_total = 0
    strong_rejected = 0
    
    borderline_total = 0
    borderline_accepted = 0
    
    adversarial_total = 0
    adversarial_accepted = 0
    
    failure_categories = defaultdict(int)
    
    for r in results:
        t = r["type"]
        p = r["pass"]
        reason = r["reason"]
        
        if not p:
            # Categorize the failure
            if "TIME_HORIZON_FAILURE" in reason:
                failure_categories["TIME_HORIZON_FAILURE"] += 1
            elif "QUANTIFICATION_FAILURE" in reason:
                failure_categories["QUANTIFICATION_FAILURE"] += 1
            elif "CEO_TEST_FAILURE" in reason:
                failure_categories["CEO_TEST_FAILURE"] += 1
            elif "GENERICITY_FAILURE" in reason:
                failure_categories["GENERICITY_FAILURE"] += 1
            else:
                failure_categories["OTHER"] += 1

        if t == "generic":
            generic_total += 1
            if p:
                generic_accepted += 1
        elif t == "strong":
            strong_total += 1
            if not p:
                strong_rejected += 1
        elif t == "borderline":
            borderline_total += 1
            if p:
                borderline_accepted += 1
        elif "adversarial" in t:
            adversarial_total += 1
            if p:
                adversarial_accepted += 1

    far = (generic_accepted / generic_total) * 100 if generic_total > 0 else 0.0
    frr = (strong_rejected / strong_total) * 100 if strong_total > 0 else 0.0
    borderline_pass_rate = (borderline_accepted / borderline_total) * 100 if borderline_total > 0 else 0.0
    adv_acceptance_rate = (adversarial_accepted / adversarial_total) * 100 if adversarial_total > 0 else 0.0
    
    print("\n" + "="*50)
    print("VALIDATOR CALIBRATION RESULTS")
    print("="*50)
    print(f"Generic Benchmarks (Negatives): {generic_total}")
    print(f"Generic Accepted (False Positives): {generic_accepted}")
    print(f"Strong Benchmarks (Positives): {strong_total}")
    print(f"Strong Rejected (False Negatives): {strong_rejected}")
    print(f"Borderline Benchmarks (Unlabeled): {borderline_total}")
    print(f"Borderline Accepted: {borderline_accepted}")
    print(f"Adversarial Benchmarks (Negatives): {adversarial_total}")
    print(f"Adversarial Accepted (False Positives): {adversarial_accepted}")
    print("-" * 50)
    print(f"FAR (False Acceptance Rate): {far:.1f}%")
    print(f"FRR (False Rejection Rate): {frr:.1f}%")
    print(f"Borderline Pass Rate: {borderline_pass_rate:.1f}%")
    print(f"Adversarial Acceptance Rate: {adv_acceptance_rate:.1f}%")
    print("-" * 50)
    print("Failure Categories (Across All Rejects):")
    for cat, count in failure_categories.items():
        print(f"  - {cat}: {count}")
    print("="*50)
    
    print("Audit complete! Results saved to validator_audit_results.json")

if __name__ == "__main__":
    run_audit()
