#!/usr/bin/env python3
"""
Disk Usage Monitor Application
Main entry point for the disk usage monitoring application.
"""

import sys
import os
import time
import signal
import threading
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config_manager import ConfigManager
from disk_monitor import DiskMonitor
from email_notifier import EmailNotifier
from alert_manager import AlertManager
from logger import Logger
from web_dashboard import WebDashboard


class DiskUsageMonitorApp:
    def __init__(self):
        self.running = False
        self.config_manager = None
        self.logger = None
        self.disk_monitor = None
        self.email_notifier = None
        self.alert_manager = None
        self.web_dashboard = None
        self.monitor_thread = None

    def initialize(self):
        """Initialize all components."""
        try:
            # Initialize configuration manager
            self.config_manager = ConfigManager()
            self.config_manager.load_config()

            # Initialize logger
            self.logger = Logger(self.config_manager.get_logging_config())
            self.logger.info("Disk Usage Monitor Application starting...")

            # Initialize disk monitor
            self.disk_monitor = DiskMonitor(
                self.config_manager.get_disk_monitor_config(),
                self.logger
            )

            # Initialize email notifier
            self.email_notifier = EmailNotifier(
                self.config_manager.get_email_notifier_config(),
                self.logger
            )

            # Initialize alert manager
            self.alert_manager = AlertManager(
                self.config_manager.get_disk_monitor_config(),
                self.email_notifier,
                self.logger
            )

            # Initialize web dashboard (if enabled)
            web_config = self.config_manager.get_web_dashboard_config()
            if web_config.get('enabled', False):
                self.web_dashboard = WebDashboard(
                    web_config,
                    self.disk_monitor,
                    self.alert_manager,
                    self.logger
                )

            self.logger.info("All components initialized successfully")
            return True

        except Exception as e:
            print(f"Failed to initialize application: {e}")
            return False

    def start_monitoring(self):
        """Start the disk monitoring loop."""
        if self.running:
            self.logger.warning("Monitoring is already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Disk monitoring started")

    def stop_monitoring(self):
        """Stop the disk monitoring loop."""
        if not self.running:
            self.logger.warning("Monitoring is not running")
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Disk monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        check_interval = self.config_manager.get_disk_monitor_config().get('check_interval_seconds', 300)

        while self.running:
            try:
                # Check disk usage for all configured paths
                disk_info = self.disk_monitor.check_all_paths()

                # Update web dashboard with latest data
                if self.web_dashboard:
                    self.web_dashboard.update_disk_info(disk_info)

                # Check thresholds and send alerts if needed
                self.alert_manager.check_thresholds(disk_info)

                # Wait for next check
                time.sleep(check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(min(check_interval, 60))  # Wait shorter time on error

    def start_web_dashboard(self):
        """Start the web dashboard (if enabled)."""
        if self.web_dashboard:
            self.web_dashboard.start()
            self.logger.info("Web dashboard started")

    def stop_web_dashboard(self):
        """Stop the web dashboard (if enabled)."""
        if self.web_dashboard:
            self.web_dashboard.stop()
            self.logger.info("Web dashboard stopped")

    def run(self):
        """Run the application."""
        if not self.initialize():
            return False

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Start monitoring
            self.start_monitoring()

            # Start web dashboard
            self.start_web_dashboard()

            self.logger.info("Disk Usage Monitor Application is running")
            self.logger.info("Press Ctrl+C to stop")

            # Keep main thread alive
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.stop()

        return True

    def stop(self):
        """Stop all components."""
        self.logger.info("Shutting down Disk Usage Monitor Application...")

        # Stop web dashboard
        self.stop_web_dashboard()

        # Stop monitoring
        self.stop_monitoring()

        self.logger.info("Application stopped")


def main():
    """Main entry point."""
    app = DiskUsageMonitorApp()
    return 0 if app.run() else 1


if __name__ == "__main__":
    sys.exit(main())