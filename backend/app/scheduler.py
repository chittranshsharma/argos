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
    return None