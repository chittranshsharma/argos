import sys
import os
import logging
sys.path.append(os.getcwd())

from app.agents.executive_agent import ExecutiveAgent

agent = ExecutiveAgent()

html = agent._fetch_html('https://news.google.com/rss/articles/CBMifEFVX3lxTE9UcWNHT21RRk15dzlSTTRBOGlOdmE2RHVFUndyS3lfcXpJV1lQQ2ZoTXF5VFlSZk9QLUJxNDJTQUM0c2RDLS1BQ3B6WXdiNUp1aDJEdXRGX25jQi1zdDVvVFprNG1iWWNLNGJpUzZuSFF5a3liUkZOSEt2dWY?oc=5')
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
    script.extract()
text = soup.get_text(separator="\n")
lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 30]
print("Found lines:", len(lines))
for i, l in enumerate(lines[:5]):
    print(i, l)

# Check why filter failed
relevant = []
keywords = ["ceo", "cto", "cfo", "coo", "cro", "founder", "vp", "president", "board", "head of", "chief"]
name_parts = "OpenAI".lower().split()
for line in lines:
    line_lower = line.lower()
    if any(part in line_lower for part in name_parts) and any(kw in line_lower for kw in keywords):
        relevant.append(line)

print("Relevant lines:", len(relevant))
