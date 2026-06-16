"""
Argos — Outcome Resolution Engine
Provides LLM-generated suggestions for resolving hypotheses based on evidence.
Does NOT automatically resolve them.
"""

import logging
from app.llm import get_groq_llm, llm_invoke
from app.database import get_hypothesis_evaluations, get_supabase_client
import json

logger = logging.getLogger(__name__)

def generate_resolution_suggestion(hypothesis_id: str):
    client = get_supabase_client()
    res = client.table("hypotheses").select("*").eq("id", hypothesis_id).single().execute()
    if not res.data:
        return {"error": "Hypothesis not found"}
        
    hyp = res.data
    evals = get_hypothesis_evaluations(hypothesis_id)
    
    if not evals:
        return {
            "suggested_outcome": "UNKNOWN",
            "suggested_evidence": ["No evaluations or evidence recorded yet."],
            "reasoning": "Insufficient data to make a determination."
        }
        
    evidence_str = ""
    for ev in evals[:20]: # Top 20 most recent
        evidence_str += f"- Impact {ev['impact']}: {ev['reasoning']}\n"
        
    prompt = f"""
You are the Argos Intelligence Resolution Engine.
Your job is to review the evidence trail for a specific hypothesis and suggest a final outcome.
DO NOT hallucinate. Only use the provided evidence.

Hypothesis: {hyp['title']}
Description: {hyp['description']}
Confidence: {hyp['confidence']}

Evidence Trail:
{evidence_str}

Output JSON format:
{{
  "suggested_outcome": "LIKELY CORRECT|LIKELY INCORRECT|INCONCLUSIVE",
  "suggested_evidence": ["Bullet 1 of strongest evidence", "Bullet 2 of strongest evidence"],
  "reasoning": "1-2 sentences explaining the suggestion."
}}
"""
    try:
        llm = get_groq_llm()
        response = llm_invoke(llm, prompt)
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {
            "suggested_outcome": "UNKNOWN",
            "suggested_evidence": [],
            "reasoning": "Failed to parse LLM suggestion."
        }
    except Exception as e:
        logger.error(f"Error generating resolution suggestion: {e}")
        return {
            "suggested_outcome": "UNKNOWN",
            "suggested_evidence": [],
            "reasoning": "Error generating suggestion."
        }
