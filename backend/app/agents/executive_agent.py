"""
Argos — Executive Agent
Executes high-intent boolean queries to detect and classify executive movements.
Uses NewsAPI (with Google News fallback) and full HTML parsing to strictly subtype events.
"""

import logging
import json
import re
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus
import feedparser
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import math

from app.signals.registry import SignalType
from app.llm import get_groq_llm, llm_invoke
from app.config import NEWSAPI_KEY

logger = logging.getLogger(__name__)

class ExecutiveAgent:
    """Collects executive and leadership movement signals."""

    def collect(self, company_name: str, company_id: str) -> list[dict]:
        """Fetch and extract executive movements."""
        articles = self._fetch_articles(company_name)
        if not articles or not self._check_relevance(articles, company_name):
            return []

        # Batch extraction engine
        raw_events = []
        batch_texts = []
        for article in articles:
            html = self._fetch_html(article["url"])
            if html:
                paragraphs = self._extract_relevant_paragraphs(html, company_name)
            else:
                paragraphs = ""
            
            # Fallback to article title/description if HTML extraction fails or yields nothing
            if not paragraphs:
                paragraphs = f"{article.get('title', '')}\n{article.get('description', '')}"
                
            if not paragraphs.strip():
                continue
            
            block = f"[URL: {article['url']}]\n{paragraphs.strip()}"
            batch_texts.append(block)

        if batch_texts:
            combined_text = "\n\n".join(batch_texts)
            events = self._extract_executive_events(combined_text, company_name)
            raw_events.extend(events)

        # Deduplicate and aggregate
        dedup_map = defaultdict(list)
        for event in raw_events:
            person = event.get("person", "").lower().strip()
            role = event.get("role", "").lower().strip()
            move = event.get("movement_type", "").lower().strip()
            key = f"{person}_{role}_{move}_{company_name.lower().strip()}"
            if not person or not role: 
                continue
            dedup_map[key].append(event)
        
        signals = []
        for key, events in dedup_map.items():
            base_event = events[0]
            source_count = len(events)
            source_urls = list(set([e.get("url") for e in events if e.get("url")]))
            
            payload = {
                "person": base_event.get("person", "").strip(),
                "role": base_event.get("role", "").strip(),
                "movement_type": base_event.get("movement_type", "").strip(),
                "previous_company": base_event.get("previous_company", "").strip(),
                "new_company": base_event.get("new_company", "").strip(),
                "effective_date": base_event.get("effective_date", "").strip(),
                "reason_for_leaving": base_event.get("reason_for_leaving", "").strip(),
                "source_count": source_count
            }
            


            # FINAL PERSISTENCE GUARD - SIGNAL VALIDATION V2
            if not payload.get("person") or not payload.get("role"):
                logger.warning(f"ExecutiveAgent rejected signal due to missing person/role: {json.dumps(payload)}")
                continue
                
            # Prevent hallucinated company names as person names
            if payload.get("person").lower() in company_name.lower() or company_name.lower() in payload.get("person").lower():
                logger.warning(f"ExecutiveAgent rejected signal due to hallucinated person name (matches company): {json.dumps(payload)}")
                continue
                
            allowed_movements = {"appointed", "joined", "hired", "promoted", "resigned", "departed", "stepped_down", "board_appointed", "board_departed"}
            if str(payload.get("movement_type")).lower() not in allowed_movements:
                logger.warning(f"ExecutiveAgent rejected signal due to invalid movement_type: {json.dumps(payload)}")
                continue

            # Confidence Calibration
            from app.analysis.reliability import calculate_weighted_confidence
            
            # Base extraction score is high if we have a clean movement and person/role
            extraction_score = 0.9 if payload.get("movement_type") and payload.get("role") else 0.6
            evidence_score = 0.8 # Executive events are usually definitive if found
            
            confidence, reasoning = calculate_weighted_confidence(
                source_urls=source_urls,
                source_count=source_count,
                evidence_score=evidence_score,
                extraction_score=extraction_score
            )
            
            # Add reasoning to payload
            reasoning["named_entities"] = True
            payload["confidence"] = confidence
            payload["confidence_reasoning"] = reasoning

            signals.append({
                "company_id": company_id,
                "company_name": company_name,
                "signal_type": SignalType.EXECUTIVE,
                "subtype": base_event.get("subtype", "LEADERSHIP_SURGE"),
                "title": f"{payload['person']} {payload['movement_type']} as {payload['role']}",
                "content": base_event.get("reason_for_leaving", f"Executive movement detected: {payload['movement_type']}."),
                "url": base_event.get("url"),
                "payload": payload,
                "agent": "ExecutiveAgent",
                "extraction_model": "groq-llama-3",
                "review_status": reasoning["review_status"]
            })
            
        logger.info(f"ExecutiveAgent collected {len(signals)} validated signals for {company_name}")
        return signals

    def _fetch_articles(self, company_name: str) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        
        if NEWSAPI_KEY:
            query = f'"{company_name}" AND ("CEO" OR "CTO" OR "CFO" OR "COO" OR "CRO" OR "Founder" OR "Chief Scientist" OR "VP" OR "President" OR "Head of" OR "Board") AND ("appointed" OR "resigns" OR "steps down" OR "joins" OR "hired")'
            url = f"https://newsapi.org/v2/everything?q={quote_plus(query)}&language=en&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = []
                    for a in data.get("articles", [])[:10]:
                        try:
                            pub_date = datetime.strptime(a.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            if pub_date < cutoff: continue
                        except: pub_date = None
                        
                        articles.append({
                            "title": a.get("title", ""),
                            "description": a.get("description", ""),
                            "url": a.get("url", ""),
                            "published": pub_date
                        })
                    if articles:
                        return articles
            except Exception as e:
                logger.warning(f"NewsAPI failed, falling back to RSS: {e}")
                
        # Fallback to Google News RSS
        query = f'"{company_name}" AND ("CEO" OR "CTO" OR "Founder" OR "VP" OR "Board") AND ("appointed" OR "steps down" OR "resigns" OR "joins")'
        url_encoded_query = quote_plus(query)
        google_url = f"https://news.google.com/rss/search?q={url_encoded_query}&hl=en-US&gl=US"
        articles = []
        try:
            feed = feedparser.parse(google_url)
            for entry in feed.entries[:10]:
                date_str = entry.get("published", entry.get("updated", ""))
                try:
                    parsed = feedparser._parse_date(date_str)
                    pub_date = datetime(*parsed[:6], tzinfo=timezone.utc) if parsed else None
                except: pub_date = None
                
                if pub_date and pub_date < cutoff: continue
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "url": entry.get("link", ""),
                    "published": pub_date
                })
        except Exception as e:
            logger.error(f"Google News RSS error: {e}")
            
        return articles

    def _fetch_html(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                html = resp.text
                # Google News RSS returns a redirect page. Extract the real URL if present.
                if "news.google.com" in url and 'c-wiz' in html:
                    match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>', html)
                    if match and match.group(1).startswith("http"):
                        real_url = match.group(1)
                        resp = requests.get(real_url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            return resp.text
                return html
        except Exception:
            pass
        return ""

    def _extract_relevant_paragraphs(self, html: str, company_name: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.extract()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 30]
        
        relevant = []
        exec_keywords = ["ceo", "cto", "cfo", "coo", "cro", "founder", "vp", "president", "board", "head of", "chief"]
        move_keywords = ["appointed", "joins", "joined", "hired", "resigned", "steps down", "stepped down", "departure", "departed", "promoted", "named", "elected", "leaving", "leaves"]
        name_parts = company_name.lower().split()
        for line in lines:
            line_lower = line.lower()
            has_company = any(part in line_lower for part in name_parts)
            has_exec = any(kw in line_lower for kw in exec_keywords)
            has_move = any(kw in line_lower for kw in move_keywords)
            
            if has_company and has_exec and has_move:
                relevant.append(line)
                
        return "\n".join(relevant[:10])

    def _check_relevance(self, articles: list[dict], company_name: str) -> bool:
        """Evaluate if the article batch contains relevant signals before deep scraping."""
        content = "\n".join([f"{a.get('title', '')} {a.get('description', '')}" for a in articles[:10]]).lower()
        keywords = ["ceo", "cfo", "cto", "coo", "cro", "founder", "president", "vp", "board", "appointed", "joins", "resigns", "steps down", "promotion", "hired", "departed", "leaving"]
        name_parts = company_name.lower().split()
        
        has_company = any(part in content for part in name_parts)
        has_keyword = any(kw in content for kw in keywords)
        
        return has_company and has_keyword

    def _extract_executive_events(self, text: str, company_name: str) -> list[dict]:
        if len(text.strip()) < 50:
            return []
            
        prompt = f"""Analyze the following texts from news articles about {company_name}.
Extract any major executive movements (e.g., Founder, CEO, CTO, VP Engineering, Head of AI, Board Member).

CRITICAL RULE: Do NOT extract current executives giving opinions or quotes. ONLY extract actual role changes, hirings, and departures. If the text merely mentions an existing executive without an actual job movement, return an empty array [].
Each article text starts with [URL: <url>]. You MUST include the exact URL corresponding to the extracted event in the "url" field.

Allowed Subtypes: CEO_APPOINTED, CEO_DEPARTED, CTO_APPOINTED, CTO_DEPARTED, CFO_APPOINTED, CFO_DEPARTED, COO_APPOINTED, COO_DEPARTED, CRO_APPOINTED, CRO_DEPARTED, FOUNDER_APPOINTED, FOUNDER_DEPARTED, LEADERSHIP_APPOINTED, LEADERSHIP_DEPARTED, BOARD_CHANGE

Text Batch:
{text}

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
    "url": "https://example.com/article"
}}]
If no events are found, return []."""

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                events = json.loads(match.group())
                valid_events = []
                invalid_moves = ["current", "quoted", "mentioned", "spoke", "commented", "said", "warned", "believes", ""]
                allowed_movements = {"appointed", "joined", "hired", "promoted", "resigned", "departed", "stepped_down", "board_appointed", "board_departed"}
                for e in events:
                    move = e.get("movement_type", "").lower().strip()
                    if move in invalid_moves or move not in allowed_movements:
                        logger.warning({"reason": "missing_or_invalid_movement_keyword", "llm_output": e})
                        continue
                    if not e.get("person") or not e.get("role"):
                        logger.warning({"reason": "missing_person_or_role", "llm_output": e})
                        continue
                    valid_events.append(e)
                return valid_events
            return []
        except Exception as e:
            logger.error(f"ExecutiveAgent LLM extraction failed: {e}")
            return []