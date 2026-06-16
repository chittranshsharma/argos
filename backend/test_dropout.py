import sys
import os
import logging
sys.path.append(os.getcwd())

from app.agents.news_agent import NewsAgent
from app.agents.hackernews_agent import HackerNewsAgent
from app.database import get_company_by_id, get_existing_signal_urls, save_source, save_signal
from app.pipeline.validator import SignalValidator
from app.scoring.signal_scorer import SignalScorer

logging.basicConfig(level=logging.WARNING)

company = get_company_by_id('ab4d1d45-dc2a-441f-8d85-c65e1d14cb99')
news_agent = NewsAgent()
hn_agent = HackerNewsAgent()

news_signals = news_agent.collect(keywords=["OpenAI"], company_name="OpenAI", company_id=company["id"])
hn_signals = hn_agent.collect(company_name="OpenAI", company_id=company["id"])

raw_signals = news_signals + hn_signals
print(f"Total raw: {len(raw_signals)}")

existing_urls = get_existing_signal_urls(company["id"])
validator = SignalValidator()
scorer = SignalScorer()

seen_urls = set()
reasons = {"duplicate_url": 0, "validation_fail": 0, "save_fail": 0, "success": 0}

for signal in raw_signals:
    url = signal.get("url", "")
    if url and (url in existing_urls or url in seen_urls):
        reasons["duplicate_url"] += 1
        continue
        
    agent_name = signal.get("agent", "UnknownAgent")
    validated_signal = validator.validate_and_format(signal, agent_name)
    if not validated_signal:
        reasons["validation_fail"] += 1
        continue
        
    validated_dict = validated_signal.model_dump()
    scored_dict = scorer.score_signal(validated_dict)
    
    # 3. Source extraction and Persistence
    raw_text = scored_dict.pop("raw_source_text", None)
    if raw_text and url:
        source_id = save_source({
            "url": url,
            "title": scored_dict.get("title", ""),
            "raw_text": raw_text
        })
        if source_id:
            scored_dict["source_id"] = source_id

    # 4. Save Signal to DB
    db_signal = {
        "company_id": scored_dict["company_id"],
        "company_name": scored_dict["company_name"],
        "entity_type": "COMPANY",
        "signal_type": scored_dict["signal_type"].value if hasattr(scored_dict["signal_type"], "value") else scored_dict["signal_type"],
        "subtype": scored_dict["subtype"].value if hasattr(scored_dict["subtype"], "value") else scored_dict["subtype"],
        "title": scored_dict["title"],
        "content": scored_dict["content"],
        "url": scored_dict["url"],
        "confidence": scored_dict.get("confidence", 80),
        "importance": scored_dict.get("importance", 5.0),
        "source_id": scored_dict.get("source_id"),
        "agent": scored_dict.get("agent"),
        "extraction_model": scored_dict.get("extraction_model"),
        "payload": scored_dict.get("payload", {}),
        "status": "ACTIVE",
        "is_new": True,
        "occurred_at": scored_dict.get("occurred_at")
    }
    
    try:
        saved = save_signal(db_signal)
        if saved:
            reasons["success"] += 1
            if url:
                seen_urls.add(url)
        else:
            reasons["save_fail"] += 1
            print(f"Failed to save signal: {db_signal.get('title')}")
    except Exception as e:
        reasons["save_fail"] += 1
        print(f"Exception saving signal: {e}")

print("Reasons for drop:")
print(reasons)
