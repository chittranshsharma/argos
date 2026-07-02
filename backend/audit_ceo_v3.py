import sys
import os
import logging
import json
import re
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.analysis.hypothesis_engine import HypothesisEngine
from app.llm import get_groq_llm, llm_invoke
from unittest.mock import patch

logging.basicConfig(level=logging.ERROR)

captured_rejections = []

def mock_save_snapshot(name, data):
    if name == "rejected_hypothesis_create":
        captured_rejections.append(data)

def score_hypothesis(llm, title, description):
    prompt = f"""
You are a highly demanding Fortune 500 CEO. Evaluate this competitive intelligence hypothesis.
TITLE: {title}
DESCRIPTION: {description}

Score it on 5 dimensions (1-5, where 5 is best):
1. Novelty (1=obvious news recap, 5=truly non-obvious hidden dynamic)
2. Specificity (1=vague trend, 5=highly concrete target and event)
3. Falsifiability (1=impossible to prove wrong, 5=strict observable event and deadline)
4. Strategic Value (1=so what?, 5=would change my immediate resource allocation)
5. Evidence Support (1=hallucination, 5=tight logical bridge from signals)

Return JSON ONLY:
{{
  "novelty": <int>,
  "specificity": <int>,
  "falsifiability": <int>,
  "strategic_value": <int>,
  "evidence": <int>
}}
"""
    try:
        resp = llm_invoke(llm, prompt)
        match = re.search(r"\{.*\}", resp, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return {"novelty": 1, "specificity": 1, "falsifiability": 1, "strategic_value": 1, "evidence": 1}

@patch('app.analysis.hypothesis_engine.save_analytics_snapshot', mock_save_snapshot)
def run_ceo_test():
    client = get_supabase_client()
    companies = ["OpenAI", "Anthropic", "Databricks", "Stripe", "Nvidia"]
    llm = get_groq_llm()

    total_candidates = 0
    total_stored = 0
    total_ceo_worthy = 0
    
    print("=== FULL CEO TEST V3 ===")
    
    for target in companies:
        captured_rejections.clear()
        
        res = client.table("companies").select("id").eq("name", target).execute()
        if not res.data:
            print(f"Company {target} not found.")
            continue
        company_id = res.data[0]["id"]

        sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
        signals = sig_res.data or []
        signals.sort(key=lambda x: x.get("collected_at", ""), reverse=True)

        high_imp = [s for s in signals if str(s.get("signal_type", "")).upper() != "CORRELATION"]
        for s in high_imp:
            s["importance"] = 8.0

        engine = HypothesisEngine()
        
        hypotheses = engine.generate_hypotheses(
            company_id=company_id,
            company_name=target,
            recent_signals=high_imp,
            trigger_reason="CEO Test V3"
        )
        
        metrics = engine.metrics
        c_signals = metrics.get('signals_after_compression', 0)
        t_extracted = metrics.get('tensions_extracted', 0)
        candidates = metrics.get('candidate_actions_generated', 0)
        stored = metrics.get('final_created', 0)
        
        print("\n" + "="*60)
        print(f"COMPANY: {target}")
        print("FUNNEL METRICS:")
        print(f"  Signals (compressed): {c_signals}")
        print(f"  Tensions: {t_extracted}")
        print(f"  Candidates: {candidates}")
        print(f"  Validator Rejected: {metrics.get('validator_rejected', 0)}")
        print(f"  Stored Hypotheses: {stored}")
        
        survival_rate = round(stored / candidates * 100) if candidates > 0 else 0
        print(f"  Prediction Survival Rate: {survival_rate}% ({stored}/{candidates})")
        
        total_candidates += candidates
        total_stored += stored
        
        company_ceo_worthy = 0
        
        print("\nSCORED HYPOTHESES:")
        for h in hypotheses:
            title = h.get('title')
            desc = h.get('description')
            scores = score_hypothesis(llm, title, desc)
            avg = sum(scores.values()) / 5.0
            
            # We define CEO-worthy as an average score >= 3.8
            is_worthy = avg >= 3.8
            if is_worthy:
                company_ceo_worthy += 1
                total_ceo_worthy += 1
                
            print(f"- TITLE: {title}")
            print(f"  Scores: Novelty={scores.get('novelty')}, Specificity={scores.get('specificity')}, Falsifiability={scores.get('falsifiability')}, StrategicValue={scores.get('strategic_value')}, Evidence={scores.get('evidence')} | AVG={avg:.1f} [{'CEO-WORTHY' if is_worthy else 'PASSABLE'}]")
            
        yield_rate = round(company_ceo_worthy / stored * 100) if stored > 0 else 0
        print(f"  CEO Insight Yield for {target}: {yield_rate}% ({company_ceo_worthy}/{stored})")
        print("="*60)

    print("\n\n=== FINAL RESULTS ===")
    overall_survival = round(total_stored / total_candidates * 100) if total_candidates > 0 else 0
    overall_yield = round(total_ceo_worthy / total_stored * 100) if total_stored > 0 else 0
    print(f"Overall Prediction Survival Rate: {overall_survival}% ({total_stored}/{total_candidates})")
    print(f"Overall CEO Insight Yield: {overall_yield}% ({total_ceo_worthy}/{total_stored})")
    
if __name__ == "__main__":
    run_ceo_test()
