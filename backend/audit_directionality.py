import asyncio
import json
import logging
from datetime import datetime

# Setup basic logging to suppress noisy debug logs if needed, but allow app logs
logging.basicConfig(level=logging.INFO)

from app.analysis.signal_compressor import compress_signals
from app.analysis.hypothesis_engine import HypothesisEngine
from app.llm import llm_invoke
import re

def main():
    engine = HypothesisEngine()
    company_name = "Anthropic"
    
    signals = [
        # POSITIVE SIGNALS (Talent / hiring)
        {
            "id": "sig-1",
            "title": "John Jumper joins Anthropic",
            "content": "Nobel laureate John Jumper has joined Anthropic to lead their new applied science division.",
            "source_url": "https://example.com/1",
            "published_at": datetime.utcnow().isoformat()
        },
        {
            "id": "sig-2",
            "title": "Mike Krieger appointed as Chief Product Officer at Anthropic",
            "content": "Instagram co-founder Mike Krieger has joined Anthropic to head product development.",
            "source_url": "https://example.com/2",
            "published_at": datetime.utcnow().isoformat()
        },
        
        # NEGATIVE SIGNALS (Enterprise restriction / pushback)
        {
            "id": "sig-3",
            "title": "JPMorgan restricts Anthropic access for employees",
            "content": "JPMorgan has restricted employee access to Anthropic's Claude models over data privacy concerns.",
            "source_url": "https://example.com/3",
            "published_at": datetime.utcnow().isoformat()
        },
        {
            "id": "sig-4",
            "title": "Goldman Sachs bans use of Claude in trading division",
            "content": "Goldman Sachs issued a memo banning the use of Anthropic's Claude AI for any trading-related activities.",
            "source_url": "https://example.com/4",
            "published_at": datetime.utcnow().isoformat()
        },
        
        # NEUTRAL / PRODUCT SIGNALS
        {
            "id": "sig-5",
            "title": "Anthropic launches Claude Tag",
            "content": "Anthropic has released a new feature called Claude Tag for better document organization.",
            "source_url": "https://example.com/5",
            "published_at": datetime.utcnow().isoformat()
        },
        {
            "id": "sig-6",
            "title": "Anthropic updates API pricing for Claude 3",
            "content": "Anthropic announced slight adjustments to the API pricing for the Claude 3 model family.",
            "source_url": "https://example.com/6",
            "published_at": datetime.utcnow().isoformat()
        }
    ]

    print("=" * 80)
    print("STAGE 1: RAW SIGNALS")
    print("=" * 80)
    for s in signals:
        print(f"- {s['title']}")

    print("\n" + "=" * 80)
    print("STAGE 2: COMPRESSED SUMMARY")
    print("=" * 80)
    compressed = compress_signals(signals)
    for c in compressed:
        print(f"- [{c.get('signal_type', 'UNKNOWN')}] {c.get('title')}: {c.get('summary')}")

    print("\n" + "=" * 80)
    print("STAGE 3: TENSION EXTRACTION")
    print("=" * 80)
    
    context_str = ""
    for s in compressed:
        context_str += f"- [{s.get('signal_type', 'UNKNOWN')}] {s.get('title', 'Event')}: {s.get('summary', '')}\n"

    tensions = engine._extract_tensions(context_str, company_name)
    if not tensions:
        print("NO TENSIONS EXTRACTED. Need at least 2 signals per side.")
    else:
        for i, t in enumerate(tensions, 1):
            print(f"\nTENSION {i}:")
            print(f"  Force A (Pursuing): {t.get('force_a')}")
            print(f"  Evidence A: {', '.join(t.get('evidence_a', []))}")
            print(f"  Force B (Competing): {t.get('force_b')}")
            print(f"  Evidence B: {', '.join(t.get('evidence_b', []))}")

    print("\n" + "=" * 80)
    print("STAGE 4: INTERPRETATION (HYPOTHESIS GENERATION)")
    print("=" * 80)
    
    tensions_str = ""
    for i, t in enumerate(tensions, 1):
        ev_a = "; ".join(t.get("evidence_a", []))
        ev_b = "; ".join(t.get("evidence_b", []))
        tensions_str += (
            f"\nTension {i}:\n"
            f"  Pursuing  (A): {t.get('force_a', '')}\n"
            f"  Competing (B): {t.get('force_b', '')}\n"
            f"  Evidence A: {ev_a}\n"
            f"  Evidence B: {ev_b}\n"
        )
        
    prompt = f"""
You are the Argos Intelligence Hypothesis Engine.
The trigger for this generation is: Scheduled Review

A strategic analyst has already identified the following COMPETING FORCES for {company_name}:
{tensions_str}

EXISTING HYPOTHESES for {company_name}:
None

For EACH tension above, determine:
1. Does this tension map onto an EXISTING hypothesis (same strategic intent)? → output an UPDATE action.
2. Is this tension a genuinely NEW belief not yet captured? → output a CREATE action.

For every CREATE, the hypothesis MUST:
- Name what management is BETTING ON (force_a prevailing)
- Name what they are SACRIFICING to make that bet (force_b being deprioritized)
- Predict one SPECIFIC, OBSERVABLE EVENT that would confirm the bet within 30-365 days

Return a JSON array of actions.

To update an existing hypothesis (DEDUPLICATION):
{{
  "action": "UPDATE",
  "hypothesis_id": "<exact ID of the existing hypothesis>",
  "confidence_adjustment": <float between -0.2 and 0.2>,
  "reasoning": "<1-2 sentences on why this tension supports or refutes the existing hypothesis>"
}}

To create a NEW hypothesis:
{{
  "action": "CREATE",
  "type": "EXPANSION",
  "belief": "<Declarative bet. E.g., '{company_name} is sacrificing margin to win enterprise distribution'>",
  "supporting_signals": ["<Evidence A>", "<Evidence B>"],
  "counter_evidence": ["<Evidence B, or None observed>"],
  "strategic_tradeoff": "<force_a gain> at the cost of <force_b loss>",
  "prediction": "<Specific observable event that confirms the bet>",
  "themes": ["LEADERSHIP", "GTM"],
  "confidence": 0.65,
  "predicted_time_horizon": "90_days"
}}

Output ONLY a valid JSON array. Do NOT create duplicate hypotheses.
"""
    
    response = llm_invoke(engine.llm, prompt)
    match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
    if match:
        actions_data = json.loads(match.group())
        for a in actions_data:
            print("\nCANDIDATE ACTION:")
            print(f"  Belief: {a.get('belief')}")
            print(f"  Tradeoff: {a.get('strategic_tradeoff')}")
            print(f"  Prediction: {a.get('prediction')}")
            print(f"  Supporting: {a.get('supporting_signals')}")
            print(f"  Counter: {a.get('counter_evidence')}")
    else:
        print("LLM failed to return JSON.")
        print(response)

if __name__ == "__main__":
    main()
