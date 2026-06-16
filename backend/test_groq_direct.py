import os
from dotenv import load_dotenv
load_dotenv()
groq_key = os.environ.get("GROQ_API_KEY")

import requests
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 10
}
resp = requests.post(url, headers=headers, json=data)
print("Status Code:", resp.status_code)
print("Headers:", resp.headers.get("x-ratelimit-remaining-tokens"), resp.headers.get("x-ratelimit-reset-tokens"))
print("Response:", resp.text)
