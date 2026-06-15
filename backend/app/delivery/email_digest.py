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
        Send a weekly intelligence digest email combining all company reports.
        Uses Gmail SMTP with STARTTLS.
        """
        if not self.enabled:
            logger.debug("Email disabled — skipping digest")
            return False

        recipient = recipient or self.user  # Send to self if no recipient

        try:
            # Build HTML email
            html_content = self._build_html_digest(reports)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "🔍 Argos Weekly Intelligence Digest"
            msg["From"] = self.user
            msg["To"] = recipient

            # Plain text fallback
            text_content = self._build_text_digest(reports)
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Send via Gmail SMTP
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user, self.password)
                server.sendmail(self.user, recipient, msg.as_string())

            logger.info(f"Weekly digest email sent to {recipient}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending digest: {e}")
            return False
        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            return False

    def _build_html_digest(self, reports: list[dict]) -> str:
        """Build an HTML email body from company reports."""
        company_sections = ""

        for report in reports:
            company_name = report.get("company_name", "Unknown")
            signals_analyzed = report.get("signals_analyzed", 0)
            key_findings = report.get("key_findings", [])
            report_md = report.get("report_markdown", "")

            findings_html = "".join(
                f"<li>{finding}</li>" for finding in key_findings[:5]
            )
            if not findings_html:
                findings_html = "<li>No significant findings this week.</li>"

            company_sections += f"""
            <div style="margin-bottom: 30px; padding: 20px; background: #1a1a2e; border-radius: 12px; border-left: 4px solid #3b82f6;">
                <h2 style="color: #3b82f6; margin-top: 0;">🏢 {company_name}</h2>
                <p style="color: #9ca3af;">Signals analyzed: {signals_analyzed}</p>
                <h3 style="color: #e5e7eb;">Key Findings</h3>
                <ul style="color: #d1d5db;">{findings_html}</ul>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #0a0a0a;
                    color: #e5e7eb;
                    padding: 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 700px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    padding: 30px 0;
                    border-bottom: 1px solid #1f2937;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #3b82f6;
                    font-size: 28px;
                    margin: 0;
                }}
                .header p {{
                    color: #6b7280;
                    margin-top: 8px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px 0;
                    border-top: 1px solid #1f2937;
                    margin-top: 30px;
                    color: #6b7280;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Argos Intelligence Digest</h1>
                    <p>Your weekly competitive intelligence briefing</p>
                </div>
                {company_sections}
                <div class="footer">
                    <p>Powered by Argos — Autonomous Competitive Intelligence Agent</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _build_text_digest(self, reports: list[dict]) -> str:
        """Build a plain text email body as fallback."""
        lines = ["ARGOS WEEKLY INTELLIGENCE DIGEST", "=" * 40, ""]

        for report in reports:
            company_name = report.get("company_name", "Unknown")
            signals_analyzed = report.get("signals_analyzed", 0)
            key_findings = report.get("key_findings", [])

            lines.append(f"🏢 {company_name}")
            lines.append(f"   Signals analyzed: {signals_analyzed}")
            lines.append("   Key Findings:")
            for finding in key_findings[:5]:
                lines.append(f"   • {finding}")
            lines.append("")

        lines.append("---")
        lines.append("Powered by Argos — Autonomous Competitive Intelligence Agent")
        return "\n".join(lines)