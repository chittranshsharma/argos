"""
Argos — Supabase Database Client
Singleton client with all CRUD helper methods.
Uses lazy initialization to avoid crashing on import if .env is not populated.
"""

import logging
from datetime import datetime, timezone
from supabase import create_client, Client

from app.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# ── Supabase Client Singleton ───────────────────────────────
_supabase_client: Client | None = None

def get_supabase_client() -> Client:
    """Lazy initialize the Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# ── Companies ───────────────────────────────────────────────

def get_all_companies() -> list:
    """Return all active companies."""
    try:
        client = get_supabase_client()
        response = client.table("companies").select("*").eq("is_active", True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting all companies: {e}")
        return []


def get_company_by_id(company_id: str) -> dict:
    """Return a single company by UUID."""
    try:
        client = get_supabase_client()
        response = client.table("companies").select("*").eq("id", company_id).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        return {}


def add_company(company_data: dict) -> dict:
    """Insert a new company and return it."""
    try:
        client = get_supabase_client()
        response = client.table("companies").insert(company_data).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error adding company: {e}")
        return {}


def update_company(company_id: str, updates: dict) -> dict:
    """Update a company record."""
    try:
        client = get_supabase_client()
        response = (
            client.table("companies")
            .update(updates)
            .eq("id", company_id)
            .execute()
        )
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error updating company {company_id}: {e}")
        return {}


def deactivate_company(company_id: str) -> dict:
    """Soft-delete: set is_active=False."""
    return update_company(company_id, {"is_active": False})


# ── Signals ─────────────────────────────────────────────────

def save_source(source_data: dict) -> str:
    """Insert a new source record and return its UUID."""
    try:
        client = get_supabase_client()
        response = client.table("sources").insert(source_data).execute()
        if response.data:
            return response.data[0]["id"]
    except Exception as e:
        logger.error(f"Error saving source: {e}")
    return None

def save_signal(signal_data: dict) -> dict:
    """Insert a new signal record. Packs new columns into raw_data to bypass schema cache issues."""
    try:
        client = get_supabase_client()
        
        # Move new columns to raw_data to bypass migration requirement
        db_signal = signal_data.copy()
        raw_data = db_signal.get("raw_data", {})
        
        for key in ["confidence", "subtype", "source_id", "agent", "extraction_model", "occurred_at", "payload"]:
            if key in db_signal:
                raw_data[key] = db_signal.pop(key)
                
        if "source" not in db_signal or not db_signal["source"]:
            db_signal["source"] = raw_data.get("agent", "unknown").replace("Agent", "").lower()
            
        db_signal["raw_data"] = raw_data
        
        response = client.table("signals").insert(db_signal).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error saving signal: {e}")
        return {}


def get_signals(company_id: str, limit: int = 50, source: str = None) -> list:
    """Get signals for a company, optionally filtered by source."""
    try:
        client = get_supabase_client()
        query = (
            client.table("signals")
            .select("*")
            .eq("company_id", company_id)
            .order("collected_at", desc=True)
            .limit(limit)
        )
        if source and source != "all":
            query = query.eq("source", source)
        response = query.execute()
        signals = response.data or []
        for s in signals:
            raw = s.get("raw_data", {})
            for key in ["confidence", "subtype", "source_id", "agent", "extraction_model", "occurred_at", "payload"]:
                if key in raw:
                    s[key] = raw[key]
        return signals
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        return []


def get_new_signals(company_id: str) -> list:
    """Get only unseen signals for a company."""
    try:
        client = get_supabase_client()
        response = (
            client.table("signals")
            .select("*")
            .eq("company_id", company_id)
            .eq("is_new", True)
            .order("collected_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting new signals: {e}")
        return []


def get_all_signals_feed(limit: int = 100, source: str = None,
                         importance: str = None, company_id: str = None) -> list:
    """Get latest signals across all companies with optional filters."""
    try:
        client = get_supabase_client()
        query = (
            client.table("signals")
            .select("*")
            .order("collected_at", desc=True)
            .limit(limit)
        )
        if source and source != "all":
            query = query.eq("source", source)
        if importance:
            query = query.eq("importance", importance)
        if company_id:
            query = query.eq("company_id", company_id)
        response = query.execute()
        signals = response.data or []
        for s in signals:
            raw = s.get("raw_data", {})
            for key in ["confidence", "subtype", "source_id", "agent", "extraction_model", "occurred_at", "payload"]:
                if key in raw:
                    s[key] = raw[key]
        return signals
    except Exception as e:
        logger.error(f"Error getting signals feed: {e}")
        return []


def get_existing_signal_urls(company_id: str) -> set:
    """Return set of URLs already stored for a company (for dedup)."""
    try:
        client = get_supabase_client()
        response = (
            client.table("signals")
            .select("url")
            .eq("company_id", company_id)
            .execute()
        )
        return {r["url"] for r in (response.data or []) if r.get("url")}
    except Exception as e:
        logger.error(f"Error getting existing URLs: {e}")
        return set()


def mark_signals_seen(company_id: str) -> None:
    """Mark all signals for a company as seen."""
    try:
        client = get_supabase_client()
        client.table("signals").update({"is_new": False}).eq(
            "company_id", company_id
        ).eq("is_new", True).execute()
    except Exception as e:
        logger.error(f"Error marking signals seen: {e}")


# ── Reports ─────────────────────────────────────────────────

def save_report(report_data: dict) -> None:
    """Insert a new report record."""
    try:
        client = get_supabase_client()
        client.table("reports").insert(report_data).execute()
    except Exception as e:
        logger.error(f"Error saving report: {e}")


def get_reports(company_id: str) -> list:
    """Get all reports for a company, newest first."""
    try:
        client = get_supabase_client()
        response = (
            client.table("reports")
            .select("*")
            .eq("company_id", company_id)
            .order("generated_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        return []


def get_all_reports(company_id: str = None) -> list:
    """Get all reports, optionally filtered by company."""
    try:
        client = get_supabase_client()
        query = client.table("reports").select("*").order("generated_at", desc=True)
        if company_id:
            query = query.eq("company_id", company_id)
        response = query.execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting all reports: {e}")
        return []


def get_latest_reports() -> list:
    """Get the latest report per company (for weekly digest)."""
    try:
        companies = get_all_companies()
        latest = []
        for c in companies:
            reports = get_reports(c["id"])
            if reports:
                latest.append(reports[0])
        return latest
    except Exception as e:
        logger.error(f"Failed to fetch reports for {company_id}: {e}")
        return []

def get_signal_baseline(company_id: str, source: str) -> dict:
    """
    Get historical average signal count per week for a 
    company+source combo. Used for anomaly detection.
    """
    try:
        from datetime import datetime, timedelta, timezone
        from app.database import get_supabase_client
        client = get_supabase_client()

        thirty_days_ago = (
            datetime.now(timezone.utc) - timedelta(days=30)
        ).isoformat()
        
        result = client.table("signals")\
            .select("id", count="exact")\
            .eq("company_id", company_id)\
            .eq("source", source)\
            .gte("collected_at", thirty_days_ago)\
            .execute()
        
        total = result.count or 0
        weekly_avg = total / 4.3  # 30 days / 7 days per week

        # Also get current week count
        seven_days_ago = (
            datetime.now(timezone.utc) - timedelta(days=7)
        ).isoformat()
        current_week_result = client.table("signals")\
            .select("id", count="exact")\
            .eq("company_id", company_id)\
            .eq("source", source)\
            .gte("collected_at", seven_days_ago)\
            .execute()
        current_week_count = current_week_result.count or 0

        return {"weekly_avg": weekly_avg, "total_30d": total, "current_week_count": current_week_count}
    except Exception as e:
        return {"weekly_avg": 0, "total_30d": 0, "current_week_count": 0}

def update_signal_score(signal_id: str, score: int):
    try:
        from app.database import get_supabase_client
        client = get_supabase_client()
        client.table("signals").update({"score": score}).eq("id", signal_id).execute()
    except Exception as e:
        logger.error(f"Failed to update signal score: {e}")

# ── Manual Actions ──────────────────────────────────────────────────

def save_alert(alert_data: dict) -> None:
    """Insert a new alert record."""
    try:
        client = get_supabase_client()
        client.table("alerts").insert(alert_data).execute()
    except Exception as e:
        logger.error(f"Error saving alert: {e}")


def get_unsent_alerts() -> list:
    """Get all unsent alerts."""
    try:
        client = get_supabase_client()
        response = (
            client.table("alerts")
            .select("*")
            .eq("is_sent", False)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting unsent alerts: {e}")
        return []


def mark_alert_sent(alert_id: str, channels: list[str]) -> None:
    """Mark an alert as sent and record delivery channels."""
    try:
        client = get_supabase_client()
        client.table("alerts").update({
            "is_sent": True,
            "sent_via": channels
        }).eq("id", alert_id).execute()
    except Exception as e:
        logger.error(f"Error marking alert {alert_id} sent: {e}")


def get_job_signals(company_id: str, days: int = 30) -> list:
    from datetime import datetime, timedelta, timezone
    from app.database import get_supabase_client
    client = get_supabase_client()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    result = client.table("signals")\
        .select("*")\
        .eq("company_id", company_id)\
        .eq("source", "jobs")\
        .gte("collected_at", since)\
        .execute()
    return result.data or []

def get_executive_movements(company_id: str) -> list:
    from app.database import get_supabase_client
    client = get_supabase_client()
    result = client.table("signals")\
        .select("*")\
        .eq("company_id", company_id)\
        .eq("is_executive_movement", True)\
        .order("collected_at", desc=True)\
        .execute()
    return result.data or []

# ── Alerts ───────────────────────────────────────────────────

# ── Stats ───────────────────────────────────────────────────

def get_signals_today_count() -> int:
    """Count signals collected today."""
    try:
        client = get_supabase_client()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")
        response = (
            client.table("signals")
            .select("id", count="exact")
            .gte("collected_at", today)
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting signals today: {e}")
        return 0


def get_high_priority_alert_count() -> int:
    """Count unsent high-priority alerts."""
    try:
        client = get_supabase_client()
        response = (
            client.table("alerts")
            .select("id", count="exact")
            .eq("is_sent", False)
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting high priority alerts: {e}")
        return 0


def get_total_reports_count() -> int:
    """Count total reports generated."""
    try:
        client = get_supabase_client()
        response = (
            client.table("reports")
            .select("id", count="exact")
            .execute()
        )
        return response.count or 0
    except Exception as e:
        logger.error(f"Error counting reports: {e}")
        return 0

# ── Analytics Snapshots ─────────────────────────────────────

def save_analytics_snapshot(metric_type: str, payload: dict) -> None:
    """Insert a new analytics snapshot."""
    try:
        client = get_supabase_client()
        client.table("analytics_snapshots").insert({
            "metric_type": metric_type,
            "payload_json": payload,
        }).execute()
    except Exception as e:
        logger.error(f"Error saving analytics snapshot {metric_type}: {e}")

def get_latest_analytics_snapshot(metric_type: str) -> dict:
    return {}