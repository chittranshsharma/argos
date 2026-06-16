import os, json, requests
from dotenv import load_dotenv
load_dotenv(override=True)
groq_key = os.environ.get("GROQ_API_KEY")

prompt = f"""Analyze the following text from a news article about OpenAI.
Extract any major executive movements (e.g., Founder, CEO, CTO, VP Engineering, Head of AI, Board Member).
Allowed Subtypes: CEO_APPOINTED, CEO_DEPARTED, CTO_APPOINTED, CTO_DEPARTED, CFO_APPOINTED, CFO_DEPARTED, COO_APPOINTED, COO_DEPARTED, CRO_APPOINTED, CRO_DEPARTED, FOUNDER_APPOINTED, FOUNDER_DEPARTED, LEADERSHIP_APPOINTED, LEADERSHIP_DEPARTED, BOARD_CHANGE

Text:
OpenAI robotics leader resigns over concerns about Pentagon AI deal. The head of OpenAI's robotics team, Paul Christiano, announced his departure on Friday, stating that the company's military contracts conflict with its original mission.

Return ONLY valid JSON like:
[{{
    "subtype": "LEADERSHIP_DEPARTED",
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

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 500,
    "temperature": 0.1
}

resp = requests.post(url, headers=headers, json=data)
print("Status Code:", resp.status_code)
print("Headers:", resp.headers.get("x-ratelimit-remaining-tokens"), resp.headers.get("x-ratelimit-reset-tokens"))
if resp.status_code == 200:
    print(json.dumps(resp.json()["choices"][0]["message"]["content"], indent=2))
else:
    print(resp.text)
