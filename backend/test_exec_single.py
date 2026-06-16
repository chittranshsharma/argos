import sys, os, json, re, time
sys.path.append(os.getcwd())
from app.agents.executive_agent import ExecutiveAgent
from app.llm import get_groq_llm, llm_invoke

agent = ExecutiveAgent()

# Manually fetch one article about OpenAI
html = agent._fetch_html('https://news.google.com/rss/articles/CBMifEFVX3lxTE9UcWNHT21RRk15dzlSTTRBOGlOdmE2RHVFUndyS3lfcXpJV1lQQ2ZoTXF5VFlSZk9QLUJxNDJTQUM0c2RDLS1BQ3B6WXdiNUp1aDJEdXRGX25jQi1zdDVvVFprNG1iWWNLNGJpUzZuSFF5a3liUkZOSEt2dWY?oc=5')
paras = agent._extract_relevant_paragraphs(html, "OpenAI")

# Let's see if we got paragraphs
print("Original URL: https://news.google.com/rss/articles/...")
print(f"Extracted Paragraphs:\n{paras[:500]}...\n")

if not paras:
    print("No paragraphs extracted, skipping LLM")
    sys.exit(0)

prompt = f"""Analyze the following text from a news article about OpenAI.
Extract any major executive movements (e.g., Founder, CEO, CTO, VP Engineering, Head of AI, Board Member).
Allowed Subtypes: CEO_APPOINTED, CEO_DEPARTED, CTO_APPOINTED, CTO_DEPARTED, CFO_APPOINTED, CFO_DEPARTED, COO_APPOINTED, COO_DEPARTED, CRO_APPOINTED, CRO_DEPARTED, BOARD_CHANGE, LEADERSHIP_SURGE
Text:
{paras}
Return ONLY valid JSON..."""

llm = get_groq_llm()
try:
    response = llm_invoke(llm, prompt)
    match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
    if match:
        events = json.loads(match.group())
        print("LLM JSON Output:")
        print(json.dumps(events, indent=2))
except Exception as e:
    print(f"LLM failed: {e}")
