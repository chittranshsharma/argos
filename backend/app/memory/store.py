"""
Argos — Memory Store
Supabase operations wrapper for pipeline use.
Re-exports from database module for convenience.
"""

from app.database import (
    get_all_companies,
    get_company_by_id,
    add_company,
    update_company,
    deactivate_company,
    save_signal,
    get_signals,
    get_new_signals,
    get_all_signals_feed,
    get_existing_signal_urls,
    mark_signals_seen,
    save_report,
    get_reports,
    get_all_reports,
    get_latest_reports,
    save_alert,
    get_unsent_alerts,
    mark_alert_sent,
    get_signals_today_count,
    get_high_priority_alert_count,
    get_total_reports_count,
)

__all__ = [
    "get_all_companies",
    "get_company_by_id",
    "add_company",
    "update_company",
    "deactivate_company",
    "save_signal",
    "get_signals",
    "get_new_signals",
    "get_all_signals_feed",
    "get_existing_signal_urls",
    "mark_signals_seen",
    "save_report",
    "get_reports",
    "get_all_reports",
    "get_latest_reports",
    "save_alert",
    "get_unsent_alerts",
    "mark_alert_sent",
    "get_signals_today_count",
    "get_high_priority_alert_count",
    "get_total_reports_count",
]
