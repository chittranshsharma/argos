import sys, os, json, re
sys.path.append(os.getcwd())
from app.llm import get_groq_llm, llm_invoke

paras = "OpenAI robotics leader resigns over concerns about Pentagon AI deal. The head of OpenAI's robotics team, Paul Christiano, announced his departure on Friday, stating that the company's military contracts conflict with its original mission."

print("Original URL: https://example.com/openai-robotics-leader-resigns")
print(f"Extracted Paragraphs:\n{paras}\n")

prompt = f"""Analyze the following text from a news article about OpenAI.
Extract any major executive movements (e.g., Founder, CEO, CTO, VP Engineering, Head of AI, Board Member).
Allowed Subtypes: CEO_APPOINTED, CEO_DEPARTED, CTO_APPOINTED, CTO_DEPARTED, CFO_APPOINTED, CFO_DEPARTED, COO_APPOINTED, COO_DEPARTED, CRO_APPOINTED, CRO_DEPARTED, BOARD_CHANGE, LEADERSHIP_SURGE
Text:
{paras}
Return ONLY valid JSON like:
[{{
    "subtype": "CEO_DEPARTED",
    "person": "John Doe",
    "role": "CEO",
    "movement_type": "departed",
    "previous_company": "",
    "new_company": "Unknown",
    "effective_date": "October 15, 2023",
    "reason_for_leaving": "To pursue other opportunities",
    "url": "https://example.com/openai-robotics-leader-resigns"
}}]
If no events are found, return []."""

llm = get_groq_llm()
try:
    response = llm_invoke(llm, prompt)
    match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
    if match:
        events = json.loads(match.group())
        print("LLM JSON Output:")
        print(json.dumps(events, indent=2))
        
        # Deduplication + DB shape
        from datetime import datetime, timezone
        for e in events:
            source_count = 1
            confidence = 0.70
            
            sig = {
                "company_id": "test-openai-id",
                "company_name": "OpenAI",
                "signal_type": "EXECUTIVE",
                "subtype": e.get("subtype", "LEADERSHIP_SURGE"),
                "title": f"{e.get('person')} {e.get('movement_type')} as {e.get('role')}",
                "content": e.get("reason_for_leaving", f"Executive movement detected: {e.get('movement_type')}."),
                "url": e.get("url"),
                "raw_data": {
                    "payload": {
                        "person": e.get("person"),
                        "role": e.get("role"),
                        "movement_type": e.get("movement_type"),
                        "previous_company": e.get("previous_company"),
                        "new_company": e.get("new_company"),
                        "effective_date": e.get("effective_date"),
                        "reason_for_leaving": e.get("reason_for_leaving"),
                        "source_count": source_count,
                        "confidence": round(confidence, 2)
                    },
                    "agent": "ExecutiveAgent",
                    "extraction_model": "groq-llama-3"
                }
            }
            print("\nFinal Database Payload:")
            print(json.dumps(sig, indent=2))

except Exception as e:
    print(f"LLM failed: {e}")
