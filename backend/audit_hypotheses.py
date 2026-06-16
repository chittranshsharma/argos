import json
import logging
from app.database import get_supabase_client
from app.llm import get_groq_llm, llm_invoke
import re

logging.basicConfig(level=logging.INFO)

client = get_supabase_client()
llm = get_groq_llm()

targets = ['openai', 'accenture', 'databricks']

prompt_template = """
You are a strategic intelligence auditor. Your job is to measure the quality of a generated hypothesis.

Hypothesis Title: {title}
Description: {description}
Themes: {themes}
Confidence: {confidence}

Assign a Grade based on this rubric:
A = actionable strategic belief
B = useful synthesis but not actionable
C = accurate summary of signals
D = generic observation
F = noise

Also score these on a 1-5 scale:
- specificity (1-5)
- novelty (1-5)
- actionability (1-5)

Return ONLY valid JSON:
{{
  "grade": "A/B/C/D/F",
  "specificity": 1,
  "novelty": 1,
  "actionability": 1,
  "reasoning": "Brief explanation"
}}
"""

def extract_json(response):
    try:
        return json.loads(response)
    except:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return None

def main():
    companies_res = client.table('companies').select('id, name').execute().data
    
    all_hypotheses = []
    
    for target in targets:
        company = next((c for c in companies_res if target in c['name'].lower()), None)
        if not company:
            continue
            
        hyps = client.table('hypotheses').select('*').eq('company_id', company['id']).execute().data
        for h in hyps:
            h['company_name'] = company['name']
            all_hypotheses.append(h)
            
    print(f"Auditing {len(all_hypotheses)} hypotheses...")
    
    results = []
    for h in all_hypotheses:
        prompt = prompt_template.format(
            title=h['title'],
            description=h['description'],
            themes=h['themes'],
            confidence=h['confidence']
        )
        resp = llm_invoke(llm, prompt)
        score = extract_json(resp)
        if score:
            h['evaluation'] = score
            results.append(h)
        else:
            print(f"Failed to parse for {h['title']}")
            
    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Saved audit_results.json with {len(results)} graded hypotheses.")

if __name__ == "__main__":
    main()
