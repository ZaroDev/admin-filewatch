"""
Logger module for Disk Usage Monitor Application
Provides centralized logging functionality.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Dict, Any


class Logger:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the logger.

        Args:
            config: Logging configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("DiskUsageMonitor")
        self.logger.setLevel(getattr(logging, config.get('level', 'INFO')))

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Set up formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        if config.get('console_output', True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler with rotation
        file_path = config.get('file_path')
        if file_path:
            try:
                # Ensure log directory exists
                log_dir = Path(file_path).parent
                log_dir.mkdir(parents=True, exist_ok=True)

                max_bytes = config.get('max_size_mb', 10) * 1024 * 1024
                backup_count = config.get('backup_count', 5)

                file_handler = logging.handlers.RotatingFileHandler(
                    file_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not set up file logging: {e}")

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)

    def exception(self, message: str):
        """Log an exception with traceback."""
        self.logger.exception(message)