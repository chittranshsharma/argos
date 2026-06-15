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
    return None