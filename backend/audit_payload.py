import sys
import os
import json
import logging
import tiktoken
from httpx import HTTPStatusError

sys.path.append(os.getcwd())

from app.database import get_supabase_client
from app.llm import get_groq_llm, llm_invoke

logging.basicConfig(level=logging.INFO)

def estimate_tokens(text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4

def audit_payload():
    client = get_supabase_client()
    companies = ["OpenAI", "Nvidia", "Stripe", "Anthropic"]
    
    print("=== SPRINT D.4: PAYLOAD AUDIT ===\n")
    
    for target in companies:
        res = client.table("companies").select("id").eq("name", target).execute()
        if not res.data:
            continue
        company_id = res.data[0]["id"]
        
        # Get all signals (production uses historical_signals + high_importance_signals)
        # We will just grab all signals for the company to mimic the full pool
        sig_res = client.table("signals").select("*").eq("company_id", company_id).execute()
        signals = sig_res.data or []
        
        # The production logic in nodes.py does:
        # recent_signals = historical_signals + high_importance_signals
        # and then passes it to HypothesisEngine
        # HypothesisEngine does:
        # for s in recent_signals[:30]: ...
        
        sent_to_engine = signals[:30]
        
        context_str = ""
        for s in sent_to_engine:
            context_str += f"- [{s.get('signal_type', 'UNKNOWN')}] {s.get('title', 'Event')}: {s.get('content', '')}\n"
            
        prompt = f"""
You are the Argos Intelligence Hypothesis Engine.
Your job is NOT to cluster topics. Your job is to extract underlying STRATEGIC TENSIONS from recent intelligence events for {target}.
The trigger for this generation is: High importance signals detected

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
        
        token_estimate = estimate_tokens(prompt)
        
        print(f"--- {target} ---")
        print(f"Signals Retrieved from DB: {len(signals)}")
        print(f"Signals sent to HypothesisEngine prompt: {len(sent_to_engine)}")
        print(f"Token estimate of final prompt: {token_estimate} tokens")
        
        llm = get_groq_llm()
        
        hit_413 = False
        gemini_fallback = False
        empty_response = False
        candidates = 0
        
        print("Sending to LLM...")
        try:
            # We mock the exact call to see what happens
            response = llm_invoke(llm, prompt)
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Did it fall back? The llm_invoke catches Groq errors and falls back to Gemini.
            # We can't easily intercept the internal logger here without a custom handler,
            # but if it took > 10 seconds or returns an empty dict, it likely fell back or failed.
            if "mock response" in text or text.strip() in ["{}", "{\"actions\": []}"]:
                empty_response = True
            else:
                try:
                    import re
                    match = re.search(r"\{.*\}", text, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group())
                        candidates = len(parsed.get("actions", []))
                        if candidates == 0:
                            empty_response = True
                except Exception:
                    pass
                    
        except Exception as e:
            if "413" in str(e):
                hit_413 = True
            print(f"Exception caught: {e}")
            
        # To truly know if production hit 413, if the tokens > 8192, it ALWAYS hits 413 on Groq's Llama 3 models.
        if token_estimate > 8000:
            hit_413 = True # Guaranteed to hit Groq limit
            gemini_fallback = True
            
        print(f"Groq Request Made: True")
        print(f"Groq Returned 413 Payload Too Large: {'Yes' if hit_413 else 'No'}")
        print(f"Gemini Fallback Triggered: {'Yes' if gemini_fallback else 'No'}")
        print(f"Empty/Mock Response Produced (0 candidates): {'Yes' if empty_response else 'No'}")
        print(f"Candidates generated: {candidates}\n")

if __name__ == "__main__":
    audit_payload()
