"""
Configuration Manager for Disk Usage Monitor Application
Handles loading, saving, and accessing application configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    def __init__(self, config_file: str = "config/config.json"):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.default_config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "disk_monitor": {
                "paths_to_monitor": ["C:"],
                "check_interval_seconds": 300,
                "threshold_warning_percent": 80,
                "threshold_critical_percent": 90,
                "threshold_emergency_percent": 95
            },
            "email_notifier": {
                "enabled": True,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "smtp_use_tls": True,
                "from_address": "diskmonitor@example.com",
                "to_addresses": ["admin@example.com"],
                "cooldown_minutes": 60
            },
            "logging": {
                "level": "INFO",
                "file_path": "logs/disk_monitor.log",
                "max_size_mb": 10,
                "backup_count": 5,
                "console_output": True
            },
            "web_dashboard": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 5000,
                "debug": False
            },
            "space_analyzer": {
                "scan_depth": 3,
                "min_file_size_mb": 10,
                "exclude_paths": ["$Recycle.Bin", "System Volume Information", "Windows\\Temp"],
                "exclude_file_patterns": ["*.tmp", "*.log"]
            }
        }

    def load_config(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                # Merge with defaults (file config overrides defaults)
                self.config = self._deep_merge(self.default_config, file_config)
            else:
                # Use defaults if file doesn't exist
                self.config = self.default_config.copy()
                # Create the config file with defaults
                self.save_config()

            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Fall back to defaults
            self.config = self.default_config.copy()
            return False

    def save_config(self) -> bool:
        """
        Save current configuration to file.

        Returns:
            True if configuration saved successfully, False otherwise
        """
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration.

        Returns:
            Dictionary containing the full configuration
        """
        return self.config.copy()

    def get_disk_monitor_config(self) -> Dict[str, Any]:
        """Get disk monitor configuration."""
        return self.config.get("disk_monitor", {}).copy()

    def get_email_notifier_config(self) -> Dict[str, Any]:
        """Get email notifier configuration."""
        return self.config.get("email_notifier", {}).copy()

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get("logging", {}).copy()

    def get_web_dashboard_config(self) -> Dict[str, Any]:
        """Get web dashboard configuration."""
        return self.config.get("web_dashboard", {}).copy()

    def get_space_analyzer_config(self) -> Dict[str, Any]:
        """Get space analyzer configuration."""
        return self.config.get("space_analyzer", {}).copy()

    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates to apply

        Returns:
            True if configuration updated successfully, False otherwise
        """
        try:
            self.config = self._deep_merge(self.config, updates)
            return self.save_config()
        except Exception as e:
            print(f"Error updating configuration: {e}")
            return False

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.

        Args:
            base: Base dictionary
            update: Dictionary with updates to apply

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def validate_config(self) -> tuple[bool, list[str]]:
        """
        Validate the current configuration.

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Validate disk monitor config
        disk_config = self.config.get("disk_monitor", {})
        paths = disk_config.get("paths_to_monitor", [])
        if not isinstance(paths, list) or not paths:
            errors.append("disk_monitor.paths_to_monitor must be a non-empty list")

        interval = disk_config.get("check_interval_seconds")
        if not isinstance(interval, (int, float)) or interval <= 0:
            errors.append("disk_monitor.check_interval_seconds must be a positive number")

        for threshold in ["threshold_warning_percent", "threshold_critical_percent", "threshold_emergency_percent"]:
            value = disk_config.get(threshold)
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                errors.append(f"disk_monitor.{threshold} must be a number between 0 and 100")

        # Validate thresholds are in ascending order
        warn = disk_config.get("threshold_warning_percent", 0)
        critical = disk_config.get("threshold_critical_percent", 0)
        emergency = disk_config.get("threshold_emergency_percent", 0)
        if not (warn <= critical <= emergency):
            errors.append("Disk thresholds must be in ascending order: warning <= critical <= emergency")

        # Validate email notifier config
        email_config = self.config.get("email_notifier", {})
        if email_config.get("enabled", False):
            smtp_server = email_config.get("smtp_server")
            if not smtp_server or not isinstance(smtp_server, str):
                errors.append("email_notifier.smtp_server is required when email notifications are enabled")

            smtp_port = email_config.get("smtp_port")
            if not isinstance(smtp_port, int) or smtp_port <= 0 or smtp_port > 65535:
                errors.append("email_notifier.smtp_port must be a valid port number (1-65535)")

            from_addr = email_config.get("from_address")
            if not from_addr or not isinstance(from_addr, str) or "@" not in from_addr:
                errors.append("email_notifier.from_address must be a valid email address")

            to_addrs = email_config.get("to_addresses", [])
            if not isinstance(to_addrs, list) or not to_addrs:
                errors.append("email_notifier.to_addresses must be a non-empty list")
            else:
                for addr in to_addrs:
                    if not isinstance(addr, str) or "@" not in addr:
                        errors.append(f"email_notifier.to_addresses contains invalid email: {addr}")

        # Validate logging config
        log_config = self.config.get("logging", {})
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level = log_config.get("level")
        if level not in valid_levels:
            errors.append(f"logging.level must be one of: {', '.join(valid_levels)}")

        max_size = log_config.get("max_size_mb")
        if not isinstance(max_size, (int, float)) or max_size <= 0:
            errors.append("logging.max_size_mb must be a positive number")

        backup_count = log_config.get("backup_count")
        if not isinstance(backup_count, int) or backup_count < 0:
            errors.append("logging.backup_count must be a non-negative integer")

        # Validate web dashboard config
        web_config = self.config.get("web_dashboard", {})
        if web_config.get("enabled", False):
            port = web_config.get("port")
            if not isinstance(port, int) or port <= 0 or port > 65535:
                errors.append("web_dashboard.port must be a valid port number (1-65535)")

        # Validate space analyzer config
        analyzer_config = self.config.get("space_analyzer", {})
        scan_depth = analyzer_config.get("scan_depth")
        if not isinstance(scan_depth, int) or scan_depth < 0:
            errors.append("space_analyzer.scan_depth must be a non-negative integer")

        min_size = analyzer_config.get("min_file_size_mb")
        if not isinstance(min_size, (int, float)) or min_size < 0:
            errors.append("space_analyzer.min_file_size_mb must be a non-negative number")

        return len(errors) == 0, errors