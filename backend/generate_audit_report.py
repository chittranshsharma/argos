import json
import logging
from app.llm import get_groq_llm, llm_invoke
from collections import defaultdict
import time

logging.basicConfig(level=logging.WARNING)

def classify_signal(llm, company, title, agent):
    prompt = f"""You are a data analyst classifying intelligence signals for the company '{company}'.
Classify the following signal based on its title and the agent that pulled it. 

Title: "{title}"
Agent: {agent}

Categories:
- "Direct": Directly about {company}
- "Competitor": Direct competitor to {company}
- "Partner": Partner or customer of {company}
- "Industry": Relevant industry trend
- "Noise": Generic industry noise (e.g., broad AI/tech news not related to {company})
- "Incorrect": Incorrect attribution (e.g., word matching error like "Stripe" matching "strips", or another company's specific news).

Return ONLY a JSON object with the fields:
"category": "<one of the categories above>",
"reason": "<short explanation of why>"
"""
    try:
        resp = llm_invoke(llm, prompt)
        start = resp.find("{")
        end = resp.rfind("}") + 1
        return json.loads(resp[start:end])
    except Exception as e:
        return {"category": "Noise", "reason": "Failed to parse"}

def run():
    with open("signal_audit_v2.json") as f:
        data = json.load(f)

    llm = get_groq_llm()
    report_lines = []
    report_lines.append("# Signal Attribution Audit Report")
    
    # We will sample up to 30 signals per company to stay within rate limits for this quick audit
    for company, signals in data.items():
        print(f"Classifying {company}...")
        sample = signals[:30]
        
        stats = defaultdict(int)
        incorrect_signals = []
        
        for sig in sample:
            time.sleep(0.1) # basic rate limit
            res = classify_signal(llm, company, sig["title"], sig["agent"])
            cat = res.get("category", "Noise")
            stats[cat] += 1
            
            if cat == "Incorrect" or cat == "Noise":
                incorrect_signals.append({
                    "title": sig["title"],
                    "url": sig["url"],
                    "agent": sig["agent"],
                    "reason": res.get("reason"),
                    "category": cat
                })
        
        total = len(sample)
        report_lines.append(f"\n## {company}")
        report_lines.append(f"**Total Signals (Sampled):** {total}")
        report_lines.append(f"- **Direct:** {stats['Direct']} ({(stats['Direct']/total)*100:.1f}%)")
        report_lines.append(f"- **Competitor:** {stats['Competitor']} ({(stats['Competitor']/total)*100:.1f}%)")
        report_lines.append(f"- **Partner:** {stats['Partner']} ({(stats['Partner']/total)*100:.1f}%)")
        report_lines.append(f"- **Industry:** {stats['Industry']} ({(stats['Industry']/total)*100:.1f}%)")
        report_lines.append(f"- **Noise:** {stats['Noise']} ({(stats['Noise']/total)*100:.1f}%)")
        report_lines.append(f"- **Incorrect:** {stats['Incorrect']} ({(stats['Incorrect']/total)*100:.1f}%)")
        
        if incorrect_signals:
            report_lines.append("\n### Contaminated / Incorrect Signals")
            for insig in incorrect_signals[:10]: # show top 10
                report_lines.append(f"\n**Title:** {insig['title']}")
                report_lines.append(f"**Source URL:** {insig['url']}")
                report_lines.append(f"**Agent:** {insig['agent']}")
                report_lines.append(f"**Category:** {insig['category']}")
                report_lines.append(f"**Why Attached:** {insig['reason']}")

    with open("signal_audit_report_v2.md", "w") as f:
        f.write("\n".join(report_lines))

if __name__ == "__main__":
    run()
