"""
Email Notifier module for Disk Usage Monitor Application
Handles sending email notifications when disk usage exceeds thresholds.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any
import time


class EmailNotifier:
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the email notifier.

        Args:
            config: Email notifier configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.enabled = config.get('enabled', False)
        self.last_sent_time = {}  # Track last sent time for each alert type/path
        self.cooldown_minutes = config.get('cooldown_minutes', 60)

    def is_enabled(self) -> bool:
        """Check if email notifications are enabled."""
        return self.enabled

    def send_alert(self, alert_type: str, subject: str, body: str,
                   path: str = None, threshold_exceeded: float = None) -> bool:
        """
        Send an email alert.

        Args:
            alert_type: Type of alert (warning, critical, emergency)
            subject: Email subject
            body: Email body
            path: Disk path that triggered the alert (optional)
            threshold_exceeded: Percentage threshold that was exceeded (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            self.logger.debug("Email notifications are disabled")
            return False

        # Check cooldown
        cooldown_key = f"{alert_type}:{path or 'general'}"
        if self._is_in_cooldown(cooldown_key):
            self.logger.debug(f"Alert {cooldown_key} is in cooldown period")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.get('from_address', 'diskmonitor@example.com')
            msg['To'] = ", ".join(self.config.get('to_addresses', ['admin@example.com']))
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add disk info if available
            if path and threshold_exceeded is not None:
                disk_info = f"\n\nDisk Path: {path}\nUsage: {threshold_exceeded:.1f}%\nTimestamp: {self._get_current_timestamp()}"
                msg.attach(MIMEText(disk_info, 'plain'))

            # Connect to SMTP server and send
            server = smtplib.SMTP(
                self.config.get('smtp_server', 'localhost'),
                self.config.get('smtp_port', 587)
            )

            if self.config.get('smtp_use_tls', True):
                server.starttls(context=ssl.create_default_context())

            username = self.config.get('smtp_username')
            password = self.config.get('smtp_password')
            if username and password:
                server.login(username, password)

            text = msg.as_string()
            server.sendmail(
                self.config.get('from_address', 'diskmonitor@example.com'),
                self.config.get('to_addresses', ['admin@example.com']),
                text
            )
            server.quit()

            # Update last sent time
            self.last_sent_time[cooldown_key] = time.time()

            self.logger.info(f"Email alert sent: {alert_type} for {path or 'system'}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False

    def send_test_email(self) -> bool:
        """
        Send a test email to verify email configuration.

        Returns:
            True if test email sent successfully, False otherwise
        """
        subject = "Disk Usage Monitor - Test Email"
        body = """This is a test email from the Disk Usage Monitor application.

If you received this email, the email notification system is configured correctly.

Application: Disk Usage Monitor
Timestamp: {timestamp}
""".format(timestamp=self._get_current_timestamp())

        return self.send_alert("test", subject, body)

    def _is_in_cooldown(self, key: str) -> bool:
        """
        Check if an alert is in cooldown period.

        Args:
            key: Cooldown key to check

        Returns:
            True if in cooldown, False otherwise
        """
        if key not in self.last_sent_time:
            return False

        last_sent = self.last_sent_time[key]
        cooldown_seconds = self.cooldown_minutes * 60
        return (time.time() - last_sent) < cooldown_seconds

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()