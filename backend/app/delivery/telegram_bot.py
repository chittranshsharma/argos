"""
Argos — Telegram Delivery
Sends real-time alerts and weekly digests via Telegram Bot API.
"""

import logging

import requests

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramDelivery:
    """Send alerts and digests via Telegram Bot API."""

    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.enabled = bool(self.token and self.chat_id)

        if not self.enabled:
            logger.info("Telegram not configured — delivery disabled")

    def send_alert(self, message: str) -> bool:
        """
        Send a single alert message via Telegram.
        Returns True if sent successfully.
        """
        if not self.enabled:
            logger.debug("Telegram disabled — skipping alert")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }
            resp = requests.post(url, json=payload, timeout=10)

            if resp.status_code == 200:
                logger.info(f"Telegram alert sent: {message[:50]}...")
                return True
            else:
                logger.error(f"Telegram API error: {resp.status_code} — {resp.text}")
                return False

        except requests.RequestException as e:
            logger.error(f"Telegram send failed: {e}")
            return False

    def send_digest(self, company_reports: list[dict]) -> bool:
        """
        Send weekly digest with key findings per company.
        One message per company to avoid Telegram message limits.
        """
        if not self.enabled:
            return False

        success = True

        # Send header
        header = "📊 *Argos Weekly Intelligence Digest*\n" + "=" * 30
        self.send_alert(header)

        for report in company_reports:
            company_name = report.get("company_name", "Unknown")
            key_findings = report.get("key_findings", [])
            signals_analyzed = report.get("signals_analyzed", 0)

            findings_text = "\n".join(f"  • {f}" for f in key_findings[:5])
            if not findings_text:
                findings_text = "  No significant findings this week."

            message = (
                f"*🏢 {company_name}*\n"
                f"Signals analyzed: {signals_analyzed}\n\n"
                f"*Key Findings:*\n{findings_text}"
            )

            if not self.send_alert(message):
                success = False

        return success