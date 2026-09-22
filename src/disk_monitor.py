"""
Disk Monitor module for Disk Usage Monitor Application
Handles monitoring disk usage and returning disk space information.
"""

import os
import shutil
from typing import Dict, List, Any
from pathlib import Path


class DiskMonitor:
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the disk monitor.

        Args:
            config: Disk monitor configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.paths_to_monitor = config.get('paths_to_monitor', ['C:'])

    def get_disk_usage(self, path: str) -> Dict[str, Any]:
        """
        Get disk usage information for a specific path.

        Args:
            path: Path to check (e.g., 'C:', '/', '/home')

        Returns:
            Dictionary with disk usage information
        """
        try:
            # Handle Windows drive letters
            if len(path) == 2 and path.endswith(':'):
                path = path + '\\'

            # Get disk usage
            usage = shutil.disk_usage(path)

            total = usage.total
            used = usage.used
            free = usage.free
            percent_used = (used / total) * 100 if total > 0 else 0

            return {
                'path': path,
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'percent_used': round(percent_used, 2),
                'percent_free': round(100 - percent_used, 2)
            }
        except Exception as e:
            self.logger.error(f"Error getting disk usage for {path}: {e}")
            return {
                'path': path,
                'total_bytes': 0,
                'used_bytes': 0,
                'free_bytes': 0,
                'percent_used': 0.0,
                'percent_free': 0.0,
                'error': str(e)
            }

    def check_all_paths(self) -> Dict[str, Any]:
        """
        Check disk usage for all configured paths.

        Returns:
            Dictionary with disk usage information for all paths
        """
        results = {}
        overall_worst = 0.0

        for path in self.paths_to_monitor:
            disk_info = self.get_disk_usage(path)
            results[path] = disk_info

            # Track worst case for overall status
            if 'percent_used' in disk_info and disk_info['percent_used'] > overall_worst:
                overall_worst = disk_info['percent_used']

        results['_summary'] = {
            'timestamp': self._get_current_timestamp(),
            'overall_percent_used': round(overall_worst, 2),
            'paths_checked': len(self.paths_to_monitor),
            'paths_successful': len([p for p in results.keys() if not p.startswith('_') and 'error' not in results[p]])
        }

        return results

    def get_disk_info_for_path(self, path: str) -> Dict[str, Any]:
        """
        Get disk usage information for a specific path (for web dashboard).

        Args:
            path: Path to check

        Returns:
            Dictionary with disk usage information
        """
        return self.get_disk_usage(path)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()