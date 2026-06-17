"""
Argos — FastAPI Entry Point
REST API with all endpoints for the Argos CI Agent.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.config import API_PORT
from app.database import (
    get_all_companies,
    get_company_by_id,
    add_company,
    deactivate_company,
    get_signals,
    get_all_signals_feed,
    get_pending_signals,
    reject_signal,
    get_reports,
    get_all_reports,
    get_signals_today_count,
    get_high_priority_alert_count,
    get_total_reports_count,
)
from app.discovery.auto_discover import AutoDiscoverer
from app.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)

# ── Configure logging ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)


# ── Lifespan ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start scheduler on startup, stop on shutdown."""
    logger.info("🚀 Argos starting up...")
    start_scheduler()
    yield
    logger.info("🛑 Argos shutting down...")
    stop_scheduler()


# ── FastAPI App ─────────────────────────────────────────────

app = FastAPI(
    title="Argos — Competitive Intelligence Agent",
    description="Autonomous system monitoring companies across 8 data sources",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ─────────────────────────────────

class AddCompanyRequest(BaseModel):
    name: str
    website: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    website: Optional[str] = None
    github_org: Optional[str] = None
    careers_url: Optional[str] = None
    reddit_sub: Optional[str] = None
    producthunt_slug: Optional[str] = None
    linkedin_url: Optional[str] = None
    changelog_url: Optional[str] = None
    news_keywords: Optional[list[str]] = None
    added_at: Optional[str] = None
    last_monitored: Optional[str] = None
    is_active: Optional[bool] = True

class RejectSignalRequest(BaseModel):
    reason: str


# ── Background task helpers ─────────────────────────────────

def run_monitoring_for_company(company: dict):
    """Run the full monitoring pipeline for a single company."""
    try:
        from app.pipeline.graph import monitoring_graph

        initial_state = {
            "company_id": company["id"],
            "company_name": company["name"],
            "company_data": company,
            "raw_signals": [],
            "new_signals": [],
            "analysis": {},
            "key_findings": [],
            "hiring_trends": [],
            "tech_signals": [],
            "report": "",
            "alerts": [],
            "entities": [],
            "relationships": [],
        }

        result = monitoring_graph.invoke(initial_state)
        signal_count = len(result.get("new_signals", []))
        logger.info(f"Monitoring complete for {company['name']}: {signal_count} new signals")

    except Exception as e:
        logger.error(f"Background monitoring failed for {company['name']}: {e}")


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    companies = get_all_companies()
    signals_today = get_signals_today_count()
    return {
        "status": "ok",
        "companies_tracked": len(companies),
        "signals_today": signals_today,
    }


# ── Companies ───────────────────────────────────────────────

@app.post("/companies")
async def create_company(request: AddCompanyRequest, background_tasks: BackgroundTasks):
    """
    Add a new company to track.
    Auto-discovers sources and triggers first monitoring run asynchronously.
    """
    from app.database import get_all_companies, add_company, get_supabase_client
    existing_companies = get_all_companies()
    for comp in existing_companies:
        if comp["name"].lower() == request.name.lower():
            raise HTTPException(status_code=400, detail="Company already exists")

    company_data = {
        "name": request.name,
        "website": request.website,
        "news_keywords": [request.name]
    }

    try:
        company = add_company(company_data)
    except Exception as e:
        logger.error(f"Failed to save company: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save company: {str(e)}")

    def run_onboarding_async(comp: dict, req_website: str):
        try:
            discoverer = AutoDiscoverer()
            sources = discoverer.discover(comp["name"], req_website)
            client = get_supabase_client()
            client.table("companies").update(sources).eq("id", comp["id"]).execute()
            comp.update(sources)
        except Exception as e:
            logger.error(f"Async AutoDiscoverer failed: {e}")
            
        try:
            from app.discovery.competitor_mapper import CompetitorMapper
            mapper = CompetitorMapper()
            competitors = mapper.discover_competitors(comp["name"], req_website)
            mapper.store_competitor_relationships(comp["name"], comp["id"], competitors)
            client = get_supabase_client()
            client.table("companies").update({
                "competitors": [c["name"] for c in competitors]
            }).eq("id", comp["id"]).execute()
        except Exception as e:
            logger.error(f"Background competitor discovery failed: {e}")
            
        run_monitoring_for_company(comp)

    if company:
        background_tasks.add_task(run_onboarding_async, company, request.website)

    return {
        "company": company,
        "status": "DISCOVERED"
    }


@app.get("/companies")
async def list_companies():
    """Return all active companies."""
    companies = get_all_companies()
    return {"companies": companies}


@app.get("/companies/{company_id}")
async def get_company(company_id: str):
    """Return company details with latest report, recent signals, and score breakdown."""
    try:
        from app.database import get_company_by_id, get_reports, get_signals, get_supabase_client, get_partnership_count
        
        company = get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        reports = get_reports(company_id)
        signals = get_signals(company_id, limit=20)

        # Get knowledge graph data
        graph_data = {"nodes": [], "links": []}
        try:
            from app.memory.graph_db import GraphDB
            graph_db = GraphDB()
            graph_data = graph_db.get_company_graph(company["name"])
            graph_db.close()
        except Exception:
            pass

        # Fetch Score Breakdown (Latest Snapshot)
        score_breakdown = None
        try:
            client = get_supabase_client()
            snap_res = client.table("analytics_snapshots")\
                .select("payload_json")\
                .eq("metric_type", f"intelligence_score:{company_id}")\
                .order("timestamp", desc=True)\
                .limit(1)\
                .execute()
            if snap_res.data:
                score_breakdown = snap_res.data[0].get("payload_json")
        except Exception as e:
            logger.warning(f"Failed to fetch score breakdown for {company_id}: {e}")

        partnerships_count = get_partnership_count(company_id)

        return {
            "company": company,
            "latest_report": reports[0] if reports else None,
            "recent_signals": signals,
            "graph_data": graph_data,
            "score_breakdown": score_breakdown,
            "partnerships_count": partnerships_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/companies/{company_id}")
async def delete_company(company_id: str):
    """Soft-delete a company (set is_active=False)."""
    try:
        result = deactivate_company(company_id)
        return {"message": "Company deactivated", "company": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies/{company_id}/competitors")
async def get_competitors(company_id: str):
    """Get competitor list for a company"""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        result = client.table("companies")\
            .select("competitors, name")\
            .eq("id", company_id)\
            .single()\
            .execute()
        return {
            "company_name": result.data["name"],
            "competitors": result.data.get("competitors", []) or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies/{company_id}/anomalies")
async def get_anomalies(company_id: str):
    """Get signal anomalies for a company"""
    try:
        from app.scoring.signal_scorer import SignalScorer
        from app.database import get_signal_baseline
        scorer = SignalScorer()
        sources = ["github", "jobs", "news", 
                   "hackernews", "linkedin", "changelog", 
                   "producthunt"]
        anomalies = []
        for source in sources:
            baseline = get_signal_baseline(company_id, source)
            anomaly = scorer.detect_anomaly(
                company_id, source, 
                baseline.get("current_week_count", 0), 
                baseline
            )
            if anomaly.get("is_anomaly"):
                anomalies.append({
                    "source": source,
                    **anomaly
                })
        return {"anomalies": anomalies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies/{company_id}/hiring-intent")
async def get_hiring_intent(company_id: str):
    """Analyze hiring patterns to infer strategic intent"""
    try:
        from app.analysis.hiring_analyzer import HiringAnalyzer
        from app.database import get_company_by_id, get_job_signals
        
        company = get_company_by_id(company_id)
        job_signals = get_job_signals(company_id)
        
        analyzer = HiringAnalyzer()
        intent = analyzer.analyze_hiring_intent(
            company["name"], job_signals
        )
        return intent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{company_id}/executives")
async def get_executive_movements_endpoint(company_id: str):
    """Get detected executive movements for a company"""
    try:
        from app.database import get_executive_movements
        movements = get_executive_movements(company_id)
        return {"movements": movements, "count": len(movements)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{company_id}/sentiment")
async def get_sentiment_timeline(
    company_id: str, 
    weeks: int = 12
):
    """Get weekly sentiment timeline for a company"""
    try:
        from app.analysis.sentiment_analyzer import SentimentAnalyzer
        from app.database import get_supabase_client
        from datetime import datetime, timedelta, timezone
        
        client = get_supabase_client()
        since = (
            datetime.now(timezone.utc) - timedelta(weeks=weeks)
        ).isoformat()
        
        signals = client.table("signals")\
            .select("*")\
            .eq("company_id", company_id)\
            .in_("source", ["hackernews"])\
            .gte("collected_at", since)\
            .execute()
        
        analyzer = SentimentAnalyzer()
        scored = analyzer.analyze_batch_sentiment(
            signals.data or []
        )
        timeline = analyzer.get_weekly_sentiment(scored, weeks)
        
        return {
            "timeline": timeline,
            "total_signals": len(scored)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{company_id}/rules")
async def get_alert_rules(company_id: str):
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        result = client.table("alert_rules")\
            .select("*")\
            .eq("company_id", company_id)\
            .order("created_at", desc=True)\
            .execute()
        return {"rules": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/companies/{company_id}/rules")
async def create_alert_rule(company_id: str, request: dict):
    """
    Body: {
      rule_name, keyword, source (optional), 
      importance_threshold (optional)
    }
    """
    try:
        from app.database import get_supabase_client, get_company_by_id
        company = get_company_by_id(company_id)
        client = get_supabase_client()
        result = client.table("alert_rules").insert({
            "company_id": company_id,
            "company_name": company["name"],
            "rule_name": request.get("rule_name"),
            "source": request.get("source", "any"),
            "keyword": request.get("keyword"),
            "importance_threshold": request.get(
                "importance_threshold", "any"
            ),
            "is_active": True
        }).execute()
        return {"rule": result.data[0] if result.data else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/companies/{company_id}/rules/{rule_id}")
async def delete_alert_rule(company_id: str, rule_id: str):
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        client.table("alert_rules")\
            .update({"is_active": False})\
            .eq("id", rule_id)\
            .execute()
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Signals ─────────────────────────────────────────────────

@app.get("/companies/{company_id}/signals")
async def get_company_signals(company_id: str, limit: int = 50, source: str = "all"):
    """Get signals for a specific company."""
    signals = get_signals(company_id, limit=limit, source=source)
    return {"signals": signals}

@app.get("/companies/{company_id}/activity_feed")
async def get_activity_feed(company_id: str, limit: int = 50):
    """Get interleaved signals, hypotheses, and evaluations."""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        
        # 1. Fetch Signals
        sig_res = client.table("signals").select("*").eq("company_id", company_id).order("collected_at", desc=True).limit(limit).execute()
        signals = sig_res.data or []
        for s in signals:
            s["activity_type"] = "signal"
            s["timestamp"] = s.get("collected_at")
            raw = s.get("raw_data", {})
            for key in ["confidence", "subtype", "source_id", "agent", "extraction_model", "occurred_at", "payload"]:
                if key in raw:
                    s[key] = raw[key]
            
        # 2. Fetch Hypotheses
        hyp_res = client.table("hypotheses").select("*").eq("company_id", company_id).order("created_at", desc=True).limit(limit).execute()
        hypotheses = hyp_res.data or []
        for h in hypotheses:
            h["activity_type"] = "hypothesis"
            h["timestamp"] = h.get("created_at")
            
        # 3. Fetch Evaluations
        evals = []
        if hypotheses:
            hyp_ids = [h["id"] for h in hypotheses]
            eval_res = client.table("hypothesis_evaluations").select("*, signals(*)").in_("hypothesis_id", hyp_ids).order("created_at", desc=True).limit(limit).execute()
            evals = eval_res.data or []
            for e in evals:
                e["activity_type"] = "evaluation"
                e["timestamp"] = e.get("created_at")
                
        # Interleave and sort
        combined = signals + hypotheses + evals
        combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Filter out rejected signals so they don't clutter the feed
        combined = [x for x in combined if not (x.get("activity_type") == "signal" and x.get("payload", {}).get("review_status") == "rejected")]
        
        return {"feed": combined[:limit]}
    except Exception as e:
        logger.error(f"Error getting activity feed for {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/signals/feed")
def api_get_signals_feed(limit: int = 100, source: str = None, importance: str = None):
    return get_all_signals_feed(limit=limit, source=source, importance=importance)

@app.get("/api/admin/signals/pending")
def api_get_pending_signals():
    """Get all signals that need manual review."""
    return get_pending_signals()

@app.post("/api/admin/signals/{signal_id}/reject")
def api_reject_signal(signal_id: str, req: RejectSignalRequest):
    """Mark a signal as rejected."""
    reject_signal(signal_id, req.reason)
    return {"status": "success"}

@app.post("/api/admin/signals/{signal_id}/approve")
def api_approve_signal(signal_id: str):
    """Mark a pending signal as auto_approved."""
    # We can just use the database's update raw_data trick to approve it
    from app.database import get_supabase_client
    client = get_supabase_client()
    response = client.table("signals").select("*").eq("id", signal_id).single().execute()
    if response.data:
        raw_data = response.data.get("raw_data", {})
        payload = raw_data.get("payload", {})
        payload["review_status"] = "auto_approved"
        raw_data["payload"] = payload
        client.table("signals").update({"raw_data": raw_data}).eq("id", signal_id).execute()
    return {"status": "success"}

@app.get("/api/analytics/sources")
def api_get_signal_sources():
    """Get breakdown of signals by agent/source."""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        # In supabase, we can't do a raw group by without RPC, so we fetch all raw data agents or use the agent column we added
        # We can just fetch all signals (or last 1000) and group them in Python for simplicity
        response = client.table("signals").select("raw_data").order("collected_at", desc=True).limit(1000).execute()
        signals = response.data or []
        counts = {}
        total = len(signals)
        for s in signals:
            agent = s.get("raw_data", {}).get("agent", "Unknown")
            counts[agent] = counts.get(agent, 0) + 1
            
        percentages = {k: round((v / total) * 100, 1) for k, v in counts.items()} if total > 0 else {}
        return {"total": total, "counts": counts, "percentages": percentages}
    except Exception as e:
        return {"error": str(e)}

@app.get("/companies/{company_id}/hypotheses")
async def get_company_hypotheses(company_id: str):
    """Get active hypotheses for a company."""
    from app.database import get_supabase_client
    client = get_supabase_client()
    res = client.table("hypotheses").select("*").eq("company_id", company_id).execute()
    return {"hypotheses": res.data or []}

@app.get("/hypotheses/{hypothesis_id}/evaluations")
async def get_evaluations(hypothesis_id: str):
    """Get evaluations/evidence for a hypothesis."""
    from app.database import get_hypothesis_evaluations
    evaluations = get_hypothesis_evaluations(hypothesis_id)
    return {"evaluations": evaluations}

@app.get("/hypotheses/{hypothesis_id}/resolution-suggestions")
async def get_resolution_suggestions(hypothesis_id: str):
    from app.analysis.resolution_engine import generate_resolution_suggestion
    sugg = generate_resolution_suggestion(hypothesis_id)
    return sugg

from pydantic import BaseModel
class ResolveRequest(BaseModel):
    outcome: str
    resolution_reason: str

@app.post("/hypotheses/{hypothesis_id}/resolve")
async def resolve_hypothesis(hypothesis_id: str, req: ResolveRequest):
    from app.database import update_hypothesis
    from datetime import datetime, timezone
    update_hypothesis(hypothesis_id, {
        "outcome": req.outcome,
        "resolution_reason": req.resolution_reason,
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if req.outcome == "CORRECT" else ("REJECTED" if req.outcome == "INCORRECT" else "ACTIVE")
    })
    return {"status": "success"}

@app.get("/strategy/hypotheses")
async def get_strategy_portfolio():
    """Get all active hypotheses across all companies, with velocity and aging computed."""
    try:
        from app.database import get_supabase_client
        from datetime import datetime, timezone, timedelta
        client = get_supabase_client()
        
        # Get active hypotheses
        res_hyp = client.table("hypotheses").select("*, companies(name)").eq("status", "ACTIVE").execute()
        hypotheses = res_hyp.data or []
        
        # Get snapshots from 7 days ago to compute velocity
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        res_snap = client.table("hypothesis_snapshots").select("*").lte("captured_at", seven_days_ago).order("captured_at", desc=True).execute()
        
        snapshots = {}
        for snap in (res_snap.data or []):
            hid = snap["hypothesis_id"]
            if hid not in snapshots:
                snapshots[hid] = snap["confidence"]
        
        now = datetime.now(timezone.utc)
        for hyp in hypotheses:
            # Velocity
            past_conf = snapshots.get(hyp["id"], hyp["confidence"])
            hyp["confidence_velocity"] = round(hyp["confidence"] - past_conf, 2)
            
            # Drift Tracking
            if hyp.get("last_evidence_at"):
                last_ev = datetime.fromisoformat(hyp["last_evidence_at"])
                days_old = (now - last_ev).days
            else:
                created = datetime.fromisoformat(hyp["created_at"])
                days_old = (now - created).days
            
            hyp["drift_status"] = "ACTIVE"
            if days_old > 45:
                hyp["drift_status"] = "STALE"
            elif days_old > 21:
                hyp["drift_status"] = "AGING"
                
        return {"hypotheses": hypotheses}
    except Exception as e:
        return {"error": str(e)}

@app.get("/analytics/scorecard")
async def get_analyst_scorecard():
    """Scorecard for hypothesis accuracy."""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        
        # We need all hypotheses that have an outcome
        res = client.table("hypotheses").select("*").execute()
        all_hyp = res.data or []
        
        total = len(all_hyp)
        resolved = [h for h in all_hyp if h.get("outcome") and h["outcome"] in ["CORRECT", "INCORRECT", "UNKNOWN"]]
        resolved_count = len(resolved)
        
        correct = [h for h in resolved if h["outcome"] == "CORRECT"]
        incorrect = [h for h in resolved if h["outcome"] == "INCORRECT"]
        
        correct_count = len(correct)
        incorrect_count = len(incorrect)
        
        if (correct_count + incorrect_count) > 0:
            global_accuracy = correct_count / (correct_count + incorrect_count)
        else:
            global_accuracy = 0
            
        by_type = {}
        for h in resolved:
            t = h.get("type", "UNKNOWN")
            if t not in by_type:
                by_type[t] = {"correct": 0, "total": 0}
            if h["outcome"] in ["CORRECT", "INCORRECT"]:
                by_type[t]["total"] += 1
                if h["outcome"] == "CORRECT":
                    by_type[t]["correct"] += 1
                    
        type_accuracy = {}
        for t, stats in by_type.items():
            if stats["total"] > 0:
                type_accuracy[t] = stats["correct"] / stats["total"]
            else:
                type_accuracy[t] = 0
                
        return {
            "total_hypotheses": total,
            "resolved_count": resolved_count,
            "resolution_rate": resolved_count / total if total > 0 else 0,
            "global_accuracy": global_accuracy,
            "correct_predictions": correct_count,
            "incorrect_predictions": incorrect_count,
            "accuracy_by_type": type_accuracy
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/signals/feed")
async def get_signal_feed(
    limit: int = 100,
    source: str = None,
    importance: str = None,
    company_id: str = None,
):
    """Get latest signals across all companies with optional filters."""
    signals = get_all_signals_feed(
        limit=limit, source=source,
        importance=importance, company_id=company_id
    )
    return {"signals": signals}


# ── Reports ─────────────────────────────────────────────────

@app.get("/companies/{company_id}/reports")
async def get_company_reports(company_id: str):
    """Get all reports for a company."""
    reports = get_reports(company_id)
    return {"reports": reports}


@app.post("/companies/{company_id}/reports/generate")
async def generate_company_report(company_id: str, background_tasks: BackgroundTasks):
    """Trigger manual report generation for a company."""
    from app.database import get_company_by_id
    company = get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    def run_report_generation():
        from app.pipeline.nodes import generate_report_node
        from app.database import get_supabase_client
        client = get_supabase_client()
        res = client.table('signals').select('*').eq('company_id', company_id).execute()
        state = {
            'company_id': company_id,
            'company_name': company['name'],
            'new_signals': res.data or [],
            'key_findings': ['Manual generation triggered.'],
            'hiring_trends': [],
            'tech_signals': []
        }
        generate_report_node(state)

    background_tasks.add_task(run_report_generation)
    return {"status": "generating"}


@app.get("/reports")
async def list_all_reports(company_id: str = None):
    """Get all reports, optionally filtered by company."""
    reports = get_all_reports(company_id=company_id)
    return {"reports": reports}

@app.delete("/reports")
async def clear_all_reports():
    """Clear all reports."""
    from app.database import get_supabase_client
    client = get_supabase_client()
    try:
        # Delete all reports. Supabase requires a filter, using a dummy one.
        client.table("reports").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Manual Actions ──────────────────────────────────────────

@app.post("/companies/{company_id}/monitor")
async def trigger_monitoring(company_id: str, background_tasks: BackgroundTasks):
    """Manually trigger monitoring for a single company."""
    try:
        company = get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        background_tasks.add_task(run_monitoring_for_company, company)
        return {"message": f"Monitoring started for {company['name']}", "status": "running"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Stats ───────────────────────────────────────────────────

@app.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    companies = get_all_companies()
    return {
        "companies_tracked": len(companies),
        "signals_today": get_signals_today_count(),
        "high_priority_alerts": get_high_priority_alert_count(),
        "reports_generated": get_total_reports_count(),
    }


# ── Analytics ───────────────────────────────────────────────

@app.get("/analytics/rankings")
async def get_analytics_rankings(limit: int = 25):
    """Get companies ranked by intelligence score with detailed metrics."""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        response = client.table("companies")\
            .select("id, name, website, intelligence_score, score_change, signals_count")\
            .eq("is_active", True)\
            .order("intelligence_score", desc=True)\
            .limit(limit)\
            .execute()
            
        rankings = []
        for index, comp in enumerate(response.data or []):
            rankings.append({
                "company": comp.get("name"),
                "score": comp.get("intelligence_score", 0.0),
                "change": comp.get("score_change", 0.0),
                "rank": index + 1,
                "signals": comp.get("signals_count", 0),
                "id": comp.get("id"),
                "website": comp.get("website")
            })
            
        return {"rankings": rankings}
    except Exception as e:
        logger.error(f"Error fetching analytics rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{company_id}/analytics")
async def get_company_analytics(company_id: str):
    """Get latest analytics snapshot and history for a company."""
    try:
        from app.database import get_supabase_client, get_latest_analytics_snapshot
        client = get_supabase_client()
        
        metric_type = f"intelligence_score:{company_id}"
        latest = get_latest_analytics_snapshot(metric_type)
        
        from datetime import datetime, timedelta, timezone
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        
        history_response = client.table("analytics_snapshots")\
            .select("payload_json, timestamp")\
            .eq("metric_type", metric_type)\
            .gte("timestamp", thirty_days_ago)\
            .order("timestamp", desc=True)\
            .execute()
            
        return {
            "current": latest,
            "history": history_response.data or []
        }
    except Exception as e:
        logger.error(f"Error fetching company analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ── Global Market Analytics ──────────────────────────────────

@app.get("/analytics/velocity")
async def get_global_velocity(days: int = 30):
    """Get global categorized signal velocity over time."""
    try:
        from app.database import get_supabase_client
        from datetime import datetime, timedelta, timezone
        from collections import defaultdict
        
        client = get_supabase_client()
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # We query the signals table to categorize
        response = client.table("signals")\
            .select("collected_at, source, is_executive_movement, title, content")\
            .gte("collected_at", start_date)\
            .execute()
            
        daily_counts = defaultdict(lambda: {"hiring": 0, "funding": 0, "launches": 0, "news": 0, "executive": 0})
        funding_keywords = ["funding", "raised", "series", "seed", "investment", "capital"]
        
        for sig in (response.data or []):
            date_str = sig.get("collected_at")[:10] if sig.get("collected_at") else None
            if not date_str: continue
            
            source = sig.get("source", "").lower()
            text = (sig.get("title", "") + " " + sig.get("content", "")).lower()
            
            # V1: keyword classification for funding
            # V2: dedicated signal taxonomy
            is_funding = any(k in text for k in funding_keywords)
            
            if sig.get("is_executive_movement"):
                daily_counts[date_str]["executive"] += 1
            elif source == "jobs":
                daily_counts[date_str]["hiring"] += 1
            elif is_funding:
                daily_counts[date_str]["funding"] += 1
            elif source in ["producthunt", "github"]:
                daily_counts[date_str]["launches"] += 1
            else:
                daily_counts[date_str]["news"] += 1
                
        # Format as array
        result = []
        for date_str in sorted(daily_counts.keys()):
            entry = {"date": date_str}
            entry.update(daily_counts[date_str])
            result.append(entry)
            
        return result
    except Exception as e:
        logger.error(f"Error fetching global velocity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/sentiment")
async def get_global_sentiment(days: int = 30):
    """Get latest company sentiment rankings."""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        
        response = client.table("companies").select("id, name, is_active").eq("is_active", True).execute()
        companies = response.data or []
        
        results = []
        for c in companies:
            comp_id = c["id"]
            metric_type = f"intelligence_score:{comp_id}"
            
            snap_res = client.table("analytics_snapshots")\
                .select("payload_json")\
                .eq("metric_type", metric_type)\
                .order("timestamp", desc=True)\
                .limit(1)\
                .execute()
                
            sentiment = 7.5 # Default neutral
            if snap_res.data and snap_res.data[0].get("payload_json"):
                payload = snap_res.data[0]["payload_json"]
                if isinstance(payload, str):
                    import json
                    try:
                        payload = json.loads(payload)
                    except:
                        pass
                sentiment = payload.get("sentiment", 7.5)
                
            results.append({
                "company_name": c["name"],
                "sentiment_score": sentiment
            })
            
        # Sort by sentiment descending
        results.sort(key=lambda x: x["sentiment_score"], reverse=True)
        return results
    except Exception as e:
        logger.error(f"Error fetching global sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/anomalies")
async def get_global_anomalies(days: int = 30):
    """Get global anomalies and critical alerts."""
    try:
        from app.database import get_supabase_client
        from datetime import datetime, timedelta, timezone
        
        client = get_supabase_client()
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        response = client.table("alerts")\
            .select("id, company_name, message, created_at, alert_type, confidence_score, impact_level")\
            .gte("created_at", start_date)\
            .neq("alert_type", "news_article")\
            .neq("alert_type", "signal")\
            .neq("alert_type", "anomaly")\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
            
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching global anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/share-of-voice")
async def get_share_of_voice(days: int = 30):
    """Get competitive share of voice (signal volume per company)."""
    try:
        from app.database import get_supabase_client
        from datetime import datetime, timedelta, timezone
        from collections import defaultdict
        
        client = get_supabase_client()
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Get active companies
        comp_res = client.table("companies").select("id, name").eq("is_active", True).execute()
        companies = {c["id"]: c["name"] for c in (comp_res.data or [])}
        
        # Get signals
        sig_res = client.table("signals").select("company_id").gte("collected_at", start_date).execute()
        
        counts = defaultdict(int)
        total = 0
        for sig in (sig_res.data or []):
            cid = sig.get("company_id")
            if cid in companies:
                counts[cid] += 1
                total += 1
                
        results = []
        for cid, count in counts.items():
            results.append({
                "company": companies[cid],
                "volume": count,
                "percentage": round((count / total * 100), 1) if total > 0 else 0
            })
            
        results.sort(key=lambda x: x["volume"], reverse=True)
        return results
    except Exception as e:
        logger.error(f"Error fetching share of voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/distribution")
async def get_intelligence_distribution():
    """Get distribution of intelligence scores."""
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        
        response = client.table("companies")\
            .select("intelligence_score")\
            .eq("is_active", True)\
            .execute()
            
        buckets = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "0-59": 0
        }
        
        for c in (response.data or []):
            score = c.get("intelligence_score", 0)
            if score >= 90: buckets["90-100"] += 1
            elif score >= 80: buckets["80-89"] += 1
            elif score >= 70: buckets["70-79"] += 1
            elif score >= 60: buckets["60-69"] += 1
            else: buckets["0-59"] += 1
            
        results = [{"range": k, "count": v} for k, v in buckets.items()]
        return results
    except Exception as e:
        logger.error(f"Error fetching intelligence distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/kpis")
async def get_global_kpis(days: int = 30):
    """Get global top-level KPIs."""
    try:
        from app.database import get_supabase_client
        from datetime import datetime, timedelta, timezone
        
        client = get_supabase_client()
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # 1. Tracked Companies
        comp_res = client.table("companies").select("id", count="exact").eq("is_active", True).execute()
        tracked_companies = comp_res.count or 0
        
        # 2. Signals Analyzed
        sig_res = client.table("signals").select("id", count="exact").gte("collected_at", start_date).execute()
        signals_analyzed = sig_res.count or 0
        
        # 3. Critical Events
        alert_res = client.table("alerts").select("id", count="exact").gte("created_at", start_date).execute()
        critical_events = alert_res.count or 0
        
        # 4. Average Global Sentiment
        response = client.table("companies").select("id").eq("is_active", True).execute()
        companies = response.data or []
        total_sentiment = 0
        count_sentiment = 0
        
        for c in companies:
            metric_type = f"intelligence_score:{c['id']}"
            snap_res = client.table("analytics_snapshots").select("payload_json").eq("metric_type", metric_type).order("timestamp", desc=True).limit(1).execute()
            if snap_res.data and snap_res.data[0].get("payload_json"):
                payload = snap_res.data[0]["payload_json"]
                if isinstance(payload, str):
                    import json
                    try: payload = json.loads(payload)
                    except: pass
                total_sentiment += payload.get("sentiment", 7.5)
                count_sentiment += 1
                
        avg_sentiment = round(total_sentiment / count_sentiment, 1) if count_sentiment > 0 else 7.5
        
        return {
            "tracked_companies": tracked_companies,
            "signals_analyzed": signals_analyzed,
            "critical_events": critical_events,
            "average_sentiment": avg_sentiment
        }
    except Exception as e:
        logger.error(f"Error fetching global KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))