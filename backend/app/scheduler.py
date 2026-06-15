"""
Argos — APScheduler Setup
Three scheduled jobs: monitoring cycle, weekly digest, real-time alerts.
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.config import MONITOR_INTERVAL_HOURS, WEEKLY_DIGEST_HOUR, ALERT_CHECK_INTERVAL_MINUTES
from app.database import (
    get_all_companies, get_unsent_alerts, mark_alert_sent,
    get_latest_reports,
)
from app.delivery.telegram_bot import TelegramDelivery
from app.delivery.email_digest import EmailDelivery

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_monitoring_cycle():
    """
    Main monitoring cycle — runs every 6 hours.
    Gets all active companies, runs the monitoring pipeline for each.
    """
    logger.info("═" * 50)
    logger.info("Starting monitoring cycle...")
    start_time = datetime.now(timezone.utc)

    try:
        # Import here to avoid circular imports
        from app.pipeline.graph import monitoring_graph

        companies = get_all_companies()
        logger.info(f"Monitoring {len(companies)} companies")

        total_signals = 0

        for company in companies:
            company_name = company.get("name", "Unknown")
            logger.info(f"─── Monitoring: {company_name} ───")

            try:
                initial_state = {
                    "company_id": company["id"],
                    "company_name": company_name,
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
                total_signals += signal_count
                logger.info(f"  ✓ {company_name}: {signal_count} new signals")

            except Exception as e:
                logger.error(f"  ✗ Monitoring failed for {company_name}: {e}")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"Monitoring cycle complete: {total_signals} signals in {elapsed:.1f}s")
        logger.info("═" * 50)

    except Exception as e:
        logger.error(f"Monitoring cycle failed: {e}")


def send_weekly_digest():
    """
    Weekly digest — sends on Monday at 9am.
    Collects latest reports and delivers via Telegram + Email.
    """
    logger.info("Generating weekly digest...")

    try:
        reports = get_latest_reports()
        if not reports:
            logger.info("No reports available for digest")
            return

        # Send via Telegram
        telegram = TelegramDelivery()
        telegram.send_digest(reports)

        # Send via Email
        email = EmailDelivery()
        email.send_weekly_digest(reports)

        logger.info(f"Weekly digest sent with {len(reports)} company reports")

    except Exception as e:
        logger.error(f"Weekly digest failed: {e}")


def send_real_time_alerts():
    """
    Alert check — runs every 15 minutes.
    Sends unsent alerts via Telegram.
    """
    try:
        unsent = get_unsent_alerts()
        if not unsent:
            return

        logger.info(f"Sending {len(unsent)} unsent alerts...")
        telegram = TelegramDelivery()

        for alert in unsent:
            message = alert.get("message", "")
            if telegram.send_alert(message):
                mark_alert_sent(alert["id"], ["telegram"])
            else:
                logger.warning(f"Failed to send alert: {alert['id']}")

    except Exception as e:
        logger.error(f"Alert sending failed: {e}")


def refresh_analytics():
    """
    Analytics Refresh — runs every 15 minutes.
    Aggregates signals and recomputes intelligence score for all companies.
    """
    logger.info("Starting analytics refresh...")
    try:
        from app.database import get_all_companies
        from app.analysis.analytics_engine import AnalyticsEngine
        
        companies = get_all_companies()
        engine = AnalyticsEngine()
        
        for company in companies:
            try:
                engine.compute_analytics(company["id"], company["name"])
            except Exception as e:
                logger.error(f"Analytics refresh failed for {company.get('name')}: {e}")
                
        logger.info(f"Analytics refresh completed for {len(companies)} companies.")
    except Exception as e:
        logger.error(f"Analytics refresh cycle failed: {e}")

def start_scheduler():
    """Configure and start the APScheduler."""
    # Job 1: Monitoring cycle every 6 hours
    scheduler.add_job(
        run_monitoring_cycle,
        trigger=IntervalTrigger(hours=MONITOR_INTERVAL_HOURS),
        id="monitoring_cycle",
        name="Company Monitoring Cycle",
        replace_existing=True,
    )

    # Job 2: Weekly digest on Mondays at 9am
    scheduler.add_job(
        send_weekly_digest,
        trigger=CronTrigger(day_of_week="mon", hour=WEEKLY_DIGEST_HOUR),
        id="weekly_digest",
        name="Weekly Intelligence Digest",
        replace_existing=True,
    )

    # Job 3: Real-time alerts every 15 minutes
    scheduler.add_job(
        send_real_time_alerts,
        trigger=IntervalTrigger(minutes=ALERT_CHECK_INTERVAL_MINUTES),
        id="real_time_alerts",
        name="Real-time Alert Check",
        replace_existing=True,
    )
    
    # Job 4: Analytics refresh every 15 minutes
    scheduler.add_job(
        refresh_analytics,
        trigger=IntervalTrigger(minutes=15),
        id="refresh_analytics",
        name="Analytics Refresh",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("APScheduler started with 4 jobs")


def stop_scheduler():
    """Shutdown the APScheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")