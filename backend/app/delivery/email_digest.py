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
    pass