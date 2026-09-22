"""
Alert Manager module for Disk Usage Monitor Application
Handles checking disk usage thresholds and triggering appropriate alerts.
"""

import time
from typing import Dict, List, Any
from datetime import datetime, timedelta


class AlertManager:
    def __init__(self, disk_config: Dict[str, Any], email_notifier, logger):
        """
        Initialize the alert manager.

        Args:
            disk_config: Disk monitor configuration dictionary
            email_notifier: EmailNotifier instance
            logger: Logger instance
        """
        self.disk_config = disk_config
        self.email_notifier = email_notifier
        self.logger = logger

        # Alert thresholds
        self.warning_threshold = disk_config.get('threshold_warning_percent', 80)
        self.critical_threshold = disk_config.get('threshold_critical_percent', 90)
        self.emergency_threshold = disk_config.get('threshold_emergency_percent', 95)

        # Alert history to prevent duplicate alerts
        self.alert_history = {}  # path -> {alert_type: last_alert_time}
        self.alert_cooldown = disk_config.get('alert_cooldown_minutes', 60) * 60  # Convert to seconds

    def check_thresholds(self, disk_info: Dict[str, Any]):
        """
        Check disk usage against thresholds and trigger alerts if needed.

        Args:
            disk_info: Disk usage information from disk monitor
        """
        # Skip summary field
        for path, info in disk_info.items():
            if path.startswith('_') or 'error' in info:
                continue

            percent_used = info.get('percent_used', 0)

            # Determine alert level
            alert_level = None
            if percent_used >= self.emergency_threshold:
                alert_level = 'emergency'
            elif percent_used >= self.critical_threshold:
                alert_level = 'critical'
            elif percent_used >= self.warning_threshold:
                alert_level = 'warning'

            # Trigger alert if needed
            if alert_level:
                self._trigger_alert(alert_level, path, percent_used, info)

    def _trigger_alert(self, alert_level: str, path: str, percent_used: float, disk_info: Dict[str, Any]):
        """
        Trigger an alert for a specific path and level.

        Args:
            alert_level: Level of alert (warning, critical, emergency)
            path: Disk path that triggered the alert
            percent_used: Percentage of disk used
            disk_info: Full disk information for the path
        """
        # Check if we should send alert based on history and cooldown
        if not self._should_send_alert(path, alert_level):
            return

        # Generate alert message
        subject, body = self._generate_alert_message(alert_level, path, percent_used, disk_info)

        # Send email alert
        if self.email_notifier.is_enabled():
            success = self.email_notifier.send_alert(
                alert_level,
                subject,
                body,
                path=path,
                threshold_exceeded=percent_used
            )

            if success:
                self._record_alert(path, alert_level)
                self.logger.info(f"{alert_level.upper()} alert sent for {path} at {percent_used:.1f}% usage")
            else:
                self.logger.error(f"Failed to send {alert_level} alert for {path}")
        else:
            self.logger.debug(f"Email notifications disabled, would send {alert_level} alert for {path}")

    def _should_send_alert(self, path: str, alert_level: str) -> bool:
        """
        Determine if an alert should be sent based on history and cooldown.

        Args:
            path: Disk path
            alert_level: Alert level

        Returns:
            True if alert should be sent, False otherwise
        """
        # Initialize history for path if needed
        if path not in self.alert_history:
            self.alert_history[path] = {}

        # Check if this alert level is in cooldown
        last_alert_time = self.alert_history[path].get(alert_level)
        if last_alert_time:
            time_since_last = time.time() - last_alert_time
            if time_since_last < self.alert_cooldown:
                return False

        return True

    def _record_alert(self, path: str, alert_level: str):
        """
        Record that an alert was sent.

        Args:
            path: Disk path
            alert_level: Alert level
        """
        if path not in self.alert_history:
            self.alert_history[path] = {}
        self.alert_history[path][alert_level] = time.time()

    def _generate_alert_message(self, alert_level: str, path: str, percent_used: float,
                              disk_info: Dict[str, Any]) -> tuple[str, str]:
        """
        Generate alert subject and body.

        Args:
            alert_level: Level of alert
            path: Disk path
            percent_used: Percentage of disk used
            disk_info: Full disk information

        Returns:
            Tuple of (subject, body)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determine alert severity description
        severity_desc = {
            'warning': 'WARNING',
            'critical': 'CRITICAL',
            'emergency': 'EMERGENCY'
        }.get(alert_level, 'UNKNOWN')

        subject = f"Disk Usage Monitor - {severity_desc} Alert: {path} at {percent_used:.1f}%"

        body = f"""
{severity_desc} ALERT - Disk Usage Monitor

Timestamp: {timestamp}
Disk Path: {path}
Current Usage: {percent_used:.1f}%
Free Space: {self._format_bytes(disk_info.get('free_bytes', 0))}
Total Space: {self._format_bytes(disk_info.get('total_bytes', 0))}
Used Space: {self._format_bytes(disk_info.get('used_bytes', 0))}

Threshold Levels:
- Warning: {self.warning_threshold}%
- Critical: {self.critical_threshold}%
- Emergency: {self.emergency_threshold}%

Please take action to free up disk space on {path} to prevent potential issues.

---
This is an automated message from the Disk Usage Monitor application.
Do not reply to this email.
""".strip()

        return subject, body

    def _format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes into human readable format.

        Args:
            bytes_value: Number of bytes

        Returns:
            Formatted string (e.g., "10.5 GB")
        """
        if bytes_value == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        while bytes_value >= 1024 and i < len(size_names) - 1:
            bytes_value /= 1024.0
            i += 1

        return f"{bytes_value:.1f} {size_names[i]}"