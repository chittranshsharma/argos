"""
Argos — Pipeline Nodes
All node functions for the LangGraph monitoring pipeline.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from app.agents.github_agent import GitHubAgent
from app.agents.news_agent import NewsAgent
from app.agents.reddit_agent import RedditAgent
from app.agents.hackernews_agent import HackerNewsAgent
from app.agents.jobs_agent import JobsAgent
from app.agents.changelog_agent import ChangelogAgent
from app.agents.producthunt_agent import ProductHuntAgent
from app.agents.linkedin_agent import LinkedInAgent
from app.database import (
    save_signal, get_existing_signal_urls, mark_signals_seen,
    save_report, save_alert, update_company,
)
from app.memory.graph_db import GraphDB
from app.llm import get_groq_llm, get_gemini_llm, llm_invoke
from app.analysis.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Node 1: Collect signals from all agents in parallel
# ═══════════════════════════════════════════════════════════

def collect_signals_node(state: dict) -> dict:
    """Run ALL agents in parallel using ThreadPoolExecutor."""
    company_data = state["company_data"]
    company_name = state["company_name"]
    company_id = state["company_id"]

    # Build agent tasks based on available company data
    tasks = []

    if company_data.get("github_org"):
        tasks.append(("github", GitHubAgent().collect,
                      {"github_org": company_data["github_org"],
                       "company_name": company_name, "company_id": company_id}))

    if company_data.get("news_keywords"):
        tasks.append(("news", NewsAgent().collect,
                      {"keywords": company_data["news_keywords"],
                       "company_name": company_name, "company_id": company_id}))

    if company_data.get("reddit_sub") or True:
        # Always search Reddit even without specific subreddit
        tasks.append(("reddit", RedditAgent().collect,
                      {"subreddit": company_data.get("reddit_sub", ""),
                       "company_name": company_name, "company_id": company_id}))

    tasks.append(("hackernews", HackerNewsAgent().collect,
                  {"company_name": company_name, "company_id": company_id}))

    if company_data.get("careers_url"):
        tasks.append(("jobs", JobsAgent().collect,
                      {"careers_url": company_data["careers_url"],
                       "company_name": company_name, "company_id": company_id}))

    from app.agents.executive_agent import ExecutiveAgent
    from app.agents.funding_agent import FundingAgent
    from app.agents.launch_agent import LaunchAgent
    from app.agents.partnership_agent import PartnershipsAgent

    # Executive
    tasks.append(("executive", ExecutiveAgent().collect,
                  {"company_name": company_name, "company_id": company_id}))

    # Funding
    tasks.append(("funding", FundingAgent().collect,
                  {"company_name": company_name, "company_id": company_id}))

    # Launch (replaces changelog and producthunt)
    tasks.append(("launch", LaunchAgent().collect,
                  {"company_name": company_name, "company_id": company_id, 
                   "producthunt_slug": company_data.get("producthunt_slug")}))

    # Partnerships
    tasks.append(("partnerships", PartnershipsAgent().collect,
                  {"company_name": company_name, "company_id": company_id}))

    if company_data.get("linkedin_url"):
        tasks.append(("linkedin", LinkedInAgent().collect,
                      {"linkedin_url": company_data["linkedin_url"],
                       "company_name": company_name, "company_id": company_id}))

    # Run all agents sequentially to respect LLM rate limits
    raw_signals = []
    agent_stats = {}

    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_name = {}
        for name, func, kwargs in tasks:
            future = executor.submit(func, **kwargs)
            future_to_name[future] = name

        for future in as_completed(future_to_name):
            agent_name = future_to_name[future]
            try:
                result = future.result(timeout=120)
                raw_signals.extend(result)
                agent_stats[agent_name] = len(result)
                logger.info(f"  ✓ {agent_name}: {len(result)} signals")
            except Exception as e:
                agent_stats[agent_name] = 0
                logger.error(f"  ✗ {agent_name} failed: {e}")

    logger.info(f"Collected {len(raw_signals)} total signals for {company_name}. "
                f"Agent stats: {agent_stats}")

    # Update last_monitored timestamp
    try:
        update_company(company_id, {"last_monitored": datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        logger.error(f"Failed to update last_monitored: {e}")

    return {"raw_signals": raw_signals}


# ═══════════════════════════════════════════════════════════
# Node 2: Filter new signals (deduplication)
# ═══════════════════════════════════════════════════════════

def filter_new_signals_node(state: dict) -> dict:
    """Compare raw_signals against existing signals and deduplicate."""
    company_id = state["company_id"]
    raw_signals = state.get("raw_signals", [])

    if not raw_signals:
        return {"new_signals": []}

    # Get existing signal URLs for dedup
    existing_urls = get_existing_signal_urls(company_id)

    from app.pipeline.validator import SignalValidator
    from app.scoring.signal_scorer import SignalScorer
    from app.database import save_source, save_signal
    
    validator = SignalValidator()
    scorer = SignalScorer()

    new_signals = []
    seen_urls = set()

    for signal in raw_signals:
        url = signal.get("url", "")
        if url and (url in existing_urls or url in seen_urls):
            continue
            
        agent_name = signal.get("agent", "UnknownAgent")
        
        # 1. Validate against Schema
        validated_signal = validator.validate_and_format(signal, agent_name)
        if not validated_signal:
            continue
            
        validated_dict = validated_signal.model_dump()
        
        # 2. Score (Confidence/Importance)
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
        # Only keep fields matching the signals table schema
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
                db_signal["id"] = saved.get("id")
                
            # Automatically create an Alert for High Importance signals
            if db_signal["importance"] >= 8.0:
                from app.database import save_alert
                alert_data = {
                    "company_id": db_signal["company_id"],
                    "company_name": db_signal["company_name"],
                    "alert_type": str(db_signal["subtype"]) if db_signal["subtype"] else str(db_signal["signal_type"]),
                    "message": f"🚨 High Priority Event ({db_signal['subtype']}): {db_signal['title']}",
                    "sent_via": [],
                    "is_sent": False,
                    "confidence_score": db_signal["confidence"],
                    "impact_level": "Critical" if db_signal["importance"] >= 9.0 else "High"
                }
                save_alert(alert_data)
                
        except Exception as e:
            logger.error(f"Error saving signal/alert: {e}")
            continue
            
        new_signals.append(db_signal)
        if url:
            seen_urls.add(url)

    logger.info(f"Filtered to {len(new_signals)} new signals "
                f"(from {len(raw_signals)} raw)")

    return {"new_signals": new_signals}


# ═══════════════════════════════════════════════════════════
# Node 3: Analyze signals with Groq LLM
# ═══════════════════════════════════════════════════════════

def analyze_signals_node(state: dict) -> dict:
    """Use Groq to analyze new signals and extract structured insights."""
    new_signals = state.get("new_signals", [])
    company_name = state["company_name"]

    if not new_signals:
        return {
            "analysis": {},
            "key_findings": [],
            "hiring_trends": [],
            "tech_signals": [],
            "entities": [],
            "relationships": [],
        }

    # Prepare signal summaries for LLM
    signal_summaries = []
    for s in new_signals[:50]:  # Limit to avoid token overflow
        signal_summaries.append(
            f"[{s.get('source', 'unknown')}] {s.get('title', '')}: "
            f"{(s.get('content', '') or '')[:200]}"
        )

    signals_text = "\n".join(signal_summaries)

    prompt = f"""You are a competitive intelligence analyst. Analyze these signals about {company_name} and return a JSON object.
    return {}