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

    with ThreadPoolExecutor(max_workers=8) as executor:
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
    from app.analysis.watchlist_scorer import WatchlistScorer
    
    validator = SignalValidator()
    scorer = SignalScorer()
    watchlist_scorer = WatchlistScorer()

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
                # Evaluate new signal against active hypotheses
                watchlist_scorer.evaluate_signal(company_id, db_signal)
                
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
# Node 2.5: Correlate Signals (Macro Events)
# ═══════════════════════════════════════════════════════════

def correlate_signals_node(state: dict) -> dict:
    """Evaluate signals over the last 60 days to identify macro-level events."""
    company_id = state["company_id"]
    company_name = state["company_name"]
    new_signals = state.get("new_signals", [])

    try:
        from app.database import get_supabase_client, save_signal, save_analytics_snapshot
        from app.analysis.signal_correlator import SignalCorrelator
        client = get_supabase_client()
        
        # Fetch 60 days of history
        import datetime
        sixty_days_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=60)).isoformat()
        res = client.table("signals").select("*").eq("company_id", company_id).gte("collected_at", sixty_days_ago).execute()
        historical_signals = res.data or []
        
        # Run correlator (EXPERIMENTAL/DORMANT - METRICS ONLY)
        correlator = SignalCorrelator()
        correlations = correlator.evaluate_correlations(company_id, company_name, historical_signals)
        
        # Save new correlations & Adjust Graph Weights
        added_correlations = []
        try:
            from app.memory.graph_db import GraphDB
            graph_db = GraphDB()
        except Exception:
            graph_db = None
            
        for c in correlations:
            # Check if we already emitted this correlation subtype for this company recently
            exists = any(s.get("subtype") == c["subtype"] for s in historical_signals if str(s.get("signal_type")).upper() == "CORRELATION")
            if not exists:
                saved = save_signal(c)
                if saved:
                    c["id"] = saved.get("id")
                    c["is_new"] = True
                    added_correlations.append(c)
                    
                    # Boost graph edge weights based on objective evidence (not creating new facts)
                    if graph_db:
                        st = c["subtype"].upper()
                        if st == "STRATEGIC_EXPANSION":
                            graph_db.boost_relationship_weight(company_name, "EXPANDING_IN", 0.3)
                            graph_db.boost_relationship_weight(company_name, "INVESTING_IN", 0.3)
                        elif st == "COMPETITIVE_ACCELERATION":
                            graph_db.boost_relationship_weight(company_name, "INVESTING_IN", 0.3)
                        elif st == "MARKET_CONSOLIDATION":
                            graph_db.boost_relationship_weight(company_name, "ACQUIRED", 0.4)
                        elif st == "ORGANIZATIONAL_RISK":
                            graph_db.boost_relationship_weight(company_name, "LED_BY", -0.2)
                        elif st == "LEADERSHIP_REORGANIZATION":
                            graph_db.boost_relationship_weight(company_name, "LED_BY", 0.2)
                        elif st == "GEOGRAPHIC_EXPANSION":
                            graph_db.boost_relationship_weight(company_name, "EXPANDING_IN", 0.3)
                            graph_db.boost_relationship_weight(company_name, "PARTNERED_WITH", 0.2)
                            
        if graph_db:
            graph_db.close()
            
        if added_correlations:
            logger.info(f"Generated {len(added_correlations)} macro-level correlations for {company_name}")
            new_signals.extend(added_correlations)
            
        # ---------------------------------------------------------------------
        # HYPOTHESIS ENGINE (Primary Strategic Layer)
        # ---------------------------------------------------------------------
        high_importance_signals = []
        for s in new_signals:
            imp = s.get("importance", 0.0)
            try:
                if float(imp) >= 5.0:
                    high_importance_signals.append(s)
            except (ValueError, TypeError):
                pass
        
        hypotheses_from_correlation = 0
        hypotheses_from_direct_signals = 0
            
        if high_importance_signals:
            try:
                from app.analysis.hypothesis_engine import HypothesisEngine
                he = HypothesisEngine()
                hypotheses = he.generate_hypotheses(
                    company_id=company_id, 
                    company_name=company_name, 
                    recent_signals=high_importance_signals + historical_signals,
                    trigger_reason="High importance signals detected"
                )
                hypotheses_from_direct_signals = len(hypotheses)
                hypothesis_metrics = he.metrics
            except Exception as e:
                logger.error(f"Failed to generate hypotheses: {e}")
                hypothesis_metrics = {}
        else:
            hypothesis_metrics = {}
                
        # ---------------------------------------------------------------------
        # STORE EXPERIMENTAL CORRELATOR METRICS
        # ---------------------------------------------------------------------
        correlation_attempts = len(correlations) if correlations else 1 # Number of times we evaluated the ruleset
        correlations_generated = len(added_correlations)
        correlation_success_rate = correlations_generated / correlation_attempts if correlation_attempts > 0 else 0
        
        save_analytics_snapshot("correlation_metrics", {
            "company_id": company_id,
            "company_name": company_name,
            "correlation_attempts": correlation_attempts,
            "correlations_generated": correlations_generated,
            "correlation_success_rate": correlation_success_rate,
            "hypotheses_from_correlation": hypotheses_from_correlation,
            "hypotheses_from_direct_signals": hypotheses_from_direct_signals,
            "hypotheses_created": hypothesis_metrics.get("hypotheses_created", 0),
            "hypotheses_deduplicated": hypothesis_metrics.get("hypotheses_deduplicated", 0),
            "evaluations_created": hypothesis_metrics.get("evaluations_created", 0),
            "confidence_updates_applied": hypothesis_metrics.get("confidence_updates_applied", 0)
        })
            
    except Exception as e:
        logger.error(f"Signal correlation failed: {e}")

    return {"new_signals": new_signals}


# ═══════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════
# Node 4: Store entities and relationships in Neo4j
# ═══════════════════════════════════════════════════════════

def store_graph_node(state: dict) -> dict:
    """Store entities and relationships in Neo4j knowledge graph."""
    entities = state.get("entities", [])
    relationships = state.get("relationships", [])
    company_name = state["company_name"]

    if not entities and not relationships:
        return {}

    try:
        graph_db = GraphDB()

        # Store entities
        for entity in entities:
            graph_db.merge_entity(
                name=entity.get("name", ""),
                entity_type=entity.get("type", "Entity"),
                description=entity.get("description", ""),
                company_name=company_name,
            )

        # Store relationships
        for rel in relationships:
            graph_db.merge_relationship(
                source=rel.get("source", ""),
                relation=rel.get("relation", "related_to"),
                target=rel.get("target", ""),
                company_name=company_name,
            )

        graph_db.close()
        logger.info(f"Stored {len(entities)} entities, {len(relationships)} relationships in Neo4j")
    except Exception as e:
        logger.error(f"Neo4j storage failed (non-fatal): {e}")

    return {}


# ═══════════════════════════════════════════════════════════
# Node 5: Generate intelligence report with Gemini
# ═══════════════════════════════════════════════════════════

def generate_report_node(state: dict) -> dict:
    """Use Gemini to generate a markdown intelligence report."""
    company_name = state["company_name"]
    company_id = state["company_id"]
    new_signals = state.get("new_signals", [])
    key_findings = state.get("key_findings", [])
    hiring_trends = state.get("hiring_trends", [])
    tech_signals = state.get("tech_signals", [])

    if not new_signals:
        return {"report": f"# {company_name} — No new signals detected this cycle."}

    # Format data for Gemini
    signals_text = "\n".join(
        f"- [{s.get('source')}] {s.get('title')}" for s in new_signals[:30]
    )
    findings_text = "\n".join(f"- {f}" for f in key_findings)
    hiring_text = json.dumps(hiring_trends, indent=2) if hiring_trends else "None detected"
    tech_text = json.dumps(tech_signals, indent=2) if tech_signals else "None detected"

    # Fetch Top Active Hypotheses instead of Correlations
    try:
        from app.database import get_active_hypotheses
        active_hypotheses = get_active_hypotheses(company_id)
        # Sort by confidence
        active_hypotheses.sort(key=lambda x: float(x.get("confidence", 0)), reverse=True)
    except Exception as e:
        logger.error(f"Failed to fetch hypotheses for report: {e}")
        active_hypotheses = []

    hypotheses_text = "\n".join(
        f"- **{h.get('title')}** (Confidence: {h.get('confidence')}): {h.get('description')}" 
        for h in active_hypotheses[:5]
    ) if active_hypotheses else "No active strategic hypotheses detected."

    raw_signals = [s for s in new_signals if str(s.get("signal_type")).upper() != "CORRELATION"]
    signals_text = "\n".join(
        f"- [{s.get('source')}] {s.get('title')} ({s.get('signal_type')})" for s in raw_signals[:30]
    )

    prompt = f"""Generate a professional competitive intelligence report in Markdown format for {company_name}.
You are writing for an Executive Analyst. Prioritize the strategic narrative derived from the Top Active Hypotheses over raw signals.

DATA:
Top Active Hypotheses:
{hypotheses_text}

Key Extracted Findings:
{findings_text}

Raw Signals ({len(raw_signals)} total):
{signals_text}

FORMAT THE REPORT EXACTLY AS FOLLOWS:

## Competitive Intelligence: {company_name}

### Executive Summary
(Write a powerful 2-3 sentence overview focusing heavily on the Top Active Hypotheses. Tell the story of what the company is strategically attempting to do or what risks they face.)

### Top Active Hypotheses
(If there are active hypotheses, list them here with their strategic implications. If none, state "No active hypotheses detected.")

### Evidence & Key Findings
(List the most important findings and evidence supporting the executive summary.)

### Raw Signals Appendix
(A clean, bulleted list of the raw signals that occurred this cycle, grouped logically.)
"""

    try:
        llm = get_groq_llm()
        report = llm_invoke(llm, prompt)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        report = f"## {company_name} — Report Generation Failed\n\nError: {str(e)[:200]}"

    # Save report to Supabase
    now = datetime.now(timezone.utc)
    report_data = {
        "company_id": company_id,
        "company_name": company_name,
        "report_markdown": report,
        "signals_analyzed": len(new_signals),
        "key_findings": key_findings,
        "hiring_trends": hiring_trends,
        "tech_signals": tech_signals,
        "generated_at": now.isoformat(),
        "period_start": (now - __import__("datetime").timedelta(days=7)).isoformat(),
        "period_end": now.isoformat(),
    }

    try:
        save_report(report_data)
    except Exception as e:
        logger.error(f"Failed to save report: {e}")

    return {"report": report}


# ═══════════════════════════════════════════════════════════
# Node 6: Generate alerts for high-importance signals
# ═══════════════════════════════════════════════════════════

def generate_alerts_node(state: dict) -> dict:
    """Create alerts for high-importance new signals."""
    new_signals = state.get("new_signals", [])
    company_name = state["company_name"]
    company_id = state["company_id"]

    alerts = []

    for signal in new_signals:
        if signal.get("importance") == "high":
            alert_data = {
                "company_id": company_id,
                "company_name": company_name,
                "alert_type": signal.get("signal_type", "signal"),
                "message": f"🚨 {company_name}: {signal.get('title', 'New signal detected')}",
                "sent_via": [],
                "is_sent": False,
                "confidence_score": 88,
                "impact_level": "High"
            }
            alerts.append(alert_data)

            try:
                save_alert(alert_data)
            except Exception as e:
                logger.error(f"Failed to save alert: {e}")

    # Evaluate custom rules
    try:
        from app.analysis.rule_engine import RuleEngine
        rule_engine = RuleEngine()
        custom_alerts = rule_engine.evaluate_rules(
            company_id,
            new_signals
        )
        for alert in custom_alerts:
            alert_data = {
                "company_id": alert["company_id"],
                "company_name": alert["company_name"],
                "alert_type": "custom_rule",
                "message": alert["message"],
                "sent_via": [],
                "is_sent": False,
                "confidence_score": 95,
                "impact_level": "Critical"
            }
            alerts.append(alert_data)
            try:
                save_alert(alert_data)
            except Exception as e:
                logger.error(f"Failed to save custom alert: {e}")
    except Exception as e:
        logger.error(f"Failed to evaluate custom rules: {e}")

    logger.info(f"Generated {len(alerts)} alerts for {company_name}")
    return {"alerts": alerts}


# ═══════════════════════════════════════════════════════════
# Node 7: Compute Analytics V1
# ═══════════════════════════════════════════════════════════

def compute_analytics_node(state: dict) -> dict:
    """Compute and store analytics metrics based on current signals."""
    company_id = state["company_id"]
    company_name = state["company_name"]
    
    try:
        engine = AnalyticsEngine()
        payload = engine.compute_analytics(company_id, company_name)
        logger.info(f"Computed analytics for {company_name}: Score {payload.get('total')}")
        return {"analysis": {**state.get("analysis", {}), "analytics": payload}}
    except Exception as e:
        logger.error(f"Failed to compute analytics for {company_name}: {e}")
        return {}



# ═══════════════════════════════════════════════════════════
# Helper
# ═══════════════════════════════════════════════════════════

def _parse_json_response(text: str) -> dict:
    """Extract and parse JSON from an LLM response."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown code fences
    import re
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object pattern
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Failed to parse JSON from LLM response")
    return {}