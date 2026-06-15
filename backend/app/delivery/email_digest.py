"""
Argos — Email Delivery
Sends weekly intelligence digest via Gmail SMTP.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import GMAIL_USER, GMAIL_APP_PASSWORD

logger = logging.getLogger(__name__)


class EmailDelivery:
    """Send weekly intelligence digest via Gmail SMTP."""

    def __init__(self):
        self.user = GMAIL_USER
        self.password = GMAIL_APP_PASSWORD
        self.enabled = bool(self.user and self.password)

        if not self.enabled:
            logger.info("Gmail not configured — email delivery disabled")

    def send_weekly_digest(self, reports: list[dict], recipient: str = None) -> bool:
        """
    pass