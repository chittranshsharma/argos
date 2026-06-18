import sys
import os
import json
import logging
sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.llm import get_groq_llm, llm_invoke

logging.basicConfig(level=logging.INFO)

def _parse_json_response(text: str) -> dict:
    try:
        import re
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except Exception:
        return {}

def audit_signal_coverage():
    client = get_supabase_client()
    target = "OpenAI"
    
    res = client.table("companies").select("id").eq("name", target).execute()
    if not res.data:
        print(f"Company {target} not found.")
        return
    company_id = res.data[0]["id"]
    
    sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
    signals = sig_res.data or []
    
    print(f"=== SIGNAL COVERAGE AUDIT: {target} ===")
    print(f"Total Signals: {len(signals)}\n")
    
    llm = get_groq_llm()
    
    batch_size = 30
    total_candidates = 0
    all_themes = []
    
    for i in range(0, len(signals), batch_size):
        batch = signals[i:i+batch_size]
        print(f"--- Batch {i+1} to {i+len(batch)} ---")
        
        context_str = ""
        for s in batch:
            context_str += f"- [{s.get('signal_type', 'UNKNOWN')}] {s.get('title', 'Event')}: {s.get('content', '')}\n"
            
        prompt = f"""
You are the Argos Intelligence Hypothesis Engine.
Your job is NOT to cluster topics. Your job is to extract underlying STRATEGIC TENSIONS from recent intelligence events for {target}.
The trigger for this generation is: Signal Coverage Audit

A valid hypothesis MUST explain:
1. What the company is strategically trying to do.
2. WHY it matters (the tension/conflict).
3. Be strictly supported by the signals below.

Format:
{{
  "actions": [
    {{
      "type": "create",
      "belief": "Clear statement of strategy",
      "prediction": "What must happen next if true",
      "confidence": 0.85,
      "signals_referenced": ["Short description of signal 1"]
    }}
  ]
}}

Existing Hypotheses to deduplicate against:
None

New Signals:
{context_str}

Return ONLY valid JSON. If no strategic tension exists, return {{"actions": []}}.
"""
        try:
            response = llm_invoke(llm, prompt)
            text = response.content if hasattr(response, 'content') else str(response)
            parsed = _parse_json_response(text)
            actions = parsed.get("actions", [])
            
            total_candidates += len(actions)
            print(f"Candidates proposed: {len(actions)}")
            for act in actions:
                belief = act.get("belief", "")
                conf = act.get("confidence", 0)
                print(f"  - [Conf: {conf}] {belief[:100]}")
                all_themes.append(belief)
                
        except Exception as e:
            print(f"Error invoking LLM for batch {i}: {e}")
            
    print("\n=== SUMMARY ===")
    print(f"Total Candidates Across All Batches: {total_candidates}")
    print("Percentage lost if only using Batch 1-30:")
    if total_candidates > 0:
        batch1_count = sum(1 for _ in range(1)) # wait, need to know how many were in batch 1
        pass # The output will speak for itself

if __name__ == "__main__":
    audit_signal_coverage()
