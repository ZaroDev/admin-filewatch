"""
Report Generator module for Disk Usage Monitor Application
Generates reports showing disk usage trends and analysis results.
"""

import json
import csv
from typing import Dict, List, Any
from datetime import datetime, timedelta
import os


class ReportGenerator:
    def __init__(self, logger):
        """
        Initialize the report generator.

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.reports_dir = "reports"
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_disk_usage_report(self, disk_info: Dict[str, Any],
                                 format_type: str = "json") -> str:
        """
        Generate a disk usage report.

        Args:
            disk_info: Disk usage information from disk monitor
            format_type: Report format (json, csv, txt)

        Returns:
            Path to the generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"disk_usage_report_{timestamp}.{format_type}"
        filepath = os.path.join(self.reports_dir, filename)

        try:
            if format_type.lower() == "json":
                return self._generate_json_report(disk_info, filepath)
            elif format_type.lower() == "csv":
                return self._generate_csv_report(disk_info, filepath)
            elif format_type.lower() == "txt":
                return self._generate_text_report(disk_info, filepath)
            else:
                # Default to JSON
                return self._generate_json_report(disk_info, filepath)
        except Exception as e:
            self.logger.error(f"Error generating {format_type} report: {e}")
            raise

    def generate_space_analysis_report(self, analysis_info: Dict[str, Any],
                                     format_type: str = "json") -> str:
        """
        Generate a space analysis report.

        Args:
            analysis_info: Space analysis information from space analyzer
            format_type: Report format (json, csv, txt)

        Returns:
            Path to the generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"space_analysis_report_{timestamp}.{format_type}"
        filepath = os.path.join(self.reports_dir, filename)

        try:
            if format_type.lower() == "json":
                return self._generate_json_space_report(analysis_info, filepath)
            elif format_type.lower() == "csv":
                return self._generate_csv_space_report(analysis_info, filepath)
            elif format_type.lower() == "txt":
                return self._generate_text_space_report(analysis_info, filepath)
            else:
                # Default to JSON
                return self._generate_json_space_report(analysis_info, filepath)
        except Exception as e:
            self.logger.error(f"Error generating space analysis {format_type} report: {e}")
            raise

    def generate_trend_report(self, historical_data: List[Dict[str, Any]],
                            format_type: str = "json") -> str:
        """
        Generate a trend report showing disk usage over time.

        Args:
            historical_data: List of disk usage snapshots over time
            format_type: Report format (json, csv, txt)

        Returns:
            Path to the generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"disk_usage_trend_report_{timestamp}.{format_type}"
        filepath = os.path.join(self.reports_dir, filename)

        try:
            if format_type.lower() == "json":
                return self._generate_json_trend_report(historical_data, filepath)
            elif format_type.lower() == "csv":
                return self._generate_csv_trend_report(historical_data, filepath)
            elif format_type.lower() == "txt":
                return self._generate_text_trend_report(historical_data, filepath)
            else:
                # Default to JSON
                return self._generate_json_trend_report(historical_data, filepath)
        except Exception as e:
            self.logger.error(f"Error generating trend {format_type} report: {e}")
            raise

    def _generate_json_report(self, disk_info: Dict[str, Any], filepath: str) -> str:
        """Generate JSON format disk usage report."""
        report_data = {
            "report_type": "disk_usage",
            "generated_at": datetime.now().isoformat(),
            "data": disk_info
        }

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"JSON disk usage report generated: {filepath}")
        return filepath

    def _generate_csv_report(self, disk_info: Dict[str, Any], filepath: str) -> str:
        """Generate CSV format disk usage report."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Path', 'Total Bytes', 'Used Bytes', 'Free Bytes',
                           'Percent Used', 'Percent Free', 'Timestamp'])

            # Write data
            for path, info in disk_info.items():
                if path.startswith('_'):
                    continue
                writer.writerow([
                    path,
                    info.get('total_bytes', 0),
                    info.get('used_bytes', 0),
                    info.get('free_bytes', 0),
                    info.get('percent_used', 0),
                    info.get('percent_free', 0),
                    info.get('timestamp', datetime.now().isoformat())
                ])

        self.logger.info(f"CSV disk usage report generated: {filepath}")
        return filepath

    def _generate_text_report(self, disk_info: Dict[str, Any], filepath: str) -> str:
        """Generate text format disk usage report."""
        with open(filepath, 'w') as f:
            f.write("DISK USAGE REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for path, info in disk_info.items():
                if path.startswith('_'):
                    continue
                f.write(f"Path: {path}\n")
                f.write(f"  Total Space: {self._format_bytes(info.get('total_bytes', 0))}\n")
                f.write(f"  Used Space:  {self._format_bytes(info.get('used_bytes', 0))}\n")
                f.write(f"  Free Space:  {self._format_bytes(info.get('free_bytes', 0))}\n")
                f.write(f"  Usage:       {info.get('percent_used', 0):.1f}%\n")
                f.write(f"  Free:        {info.get('percent_free', 0):.1f}%\n")
                f.write("-" * 30 + "\n")

            # Summary
            if '_summary' in disk_info:
                summary = disk_info['_summary']
                f.write("\nSUMMARY\n")
                f.write("-" * 30 + "\n")
                f.write(f"Overall Usage: {summary.get('overall_percent_used', 0):.1f}%\n")
                f.write(f"Paths Checked: {summary.get('paths_checked', 0)}\n")
                f.write(f"Successful:    {summary.get('paths_successful', 0)}\n")

        self.logger.info(f"Text disk usage report generated: {filepath}")
        return filepath

    def _generate_json_space_report(self, analysis_info: Dict[str, Any], filepath: str) -> str:
        """Generate JSON format space analysis report."""
        report_data = {
            "report_type": "space_analysis",
            "generated_at": datetime.now().isoformat(),
            "data": analysis_info
        }

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"JSON space analysis report generated: {filepath}")
        return filepath

    def _generate_csv_space_report(self, analysis_info: Dict[str, Any], filepath: str) -> str:
        """Generate CSV format space analysis report."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write large files section
            writer.writerow(["LARGE FILES"])
            writer.writerow(["File Path", "Size Bytes", "Size Human", "Modified Time"])

            for file_info in analysis_info.get('large_files', []):
                writer.writerow([
                    file_info.get('path', ''),
                    file_info.get('size_bytes', 0),
                    file_info.get('size_human', ''),
                    file_info.get('modified_time', '')
                ])

            writer.writerow([])  # Empty row
            writer.writerow(["LARGE FOLDERS"])
            writer.writerow(["Folder Path", "Size Bytes", "Size Human", "File Count"])

            for folder_info in analysis_info.get('large_folders', []):
                writer.writerow([
                    folder_info.get('path', ''),
                    folder_info.get('size_bytes', 0),
                    folder_info.get('size_human', ''),
                    folder_info.get('file_count', 0)
                ])

        self.logger.info(f"CSV space analysis report generated: {filepath}")
        return filepath

    def _generate_text_space_report(self, analysis_info: Dict[str, Any], filepath: str) -> str:
        """Generate text format space analysis report."""
        with open(filepath, 'w') as f:
            f.write("SPACE ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analyzed Path: {analysis_info.get('path', 'Unknown')}\n\n")

            # Large files
            f.write("LARGE FILES (Top 20)\n")
            f.write("-" * 30 + "\n")
            if analysis_info.get('large_files'):
                for i, file_info in enumerate(analysis_info['large_files'], 1):
                    f.write(f"{i:2d}. {file_info.get('path', 'Unknown')}\n")
                    f.write(f"     Size: {file_info.get('size_human', '0 B')}\n")
                    f.write(f"     Modified: {datetime.fromtimestamp(file_info.get('modified_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if file_info.get('modified_time') else 'Unknown'}\n")
                    f.write("\n")
            else:
                f.write("No large files found.\n\n")

            # Large folders
            f.write("LARGE FOLDERS (Top 20)\n")
            f.write("-" * 30 + "\n")
            if analysis_info.get('large_folders'):
                for i, folder_info in enumerate(analysis_info['large_folders'], 1):
                    f.write(f"{i:2d}. {folder_info.get('path', 'Unknown')}\n")
                    f.write(f"     Size: {folder_info.get('size_human', '0 B')}\n")
                    f.write(f"     Files: {folder_info.get('file_count', 0)}\n")
                    f.write("\n")
            else:
                f.write("No large folders found.\n\n")

            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Large Files: {analysis_info.get('total_large_files', 0)}\n")
            f.write(f"Total Large Folders: {analysis_info.get('total_large_folders', 0)}\n")
            f.write(f"Scan Time: {analysis_info.get('scan_time', 0)} seconds\n")

        self.logger.info(f"Text space analysis report generated: {filepath}")
        return filepath

    def _generate_json_trend_report(self, historical_data: List[Dict[str, Any]], filepath: str) -> str:
        """Generate JSON format trend report."""
        report_data = {
            "report_type": "disk_usage_trend",
            "generated_at": datetime.now().isoformat(),
            "data_points": len(historical_data),
            "data": historical_data
        }

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"JSON trend report generated: {filepath}")
        return filepath

    def _generate_csv_trend_report(self, historical_data: List[Dict[str, Any]], filepath: str) -> str:
        """Generate CSV format trend report."""
        if not historical_data:
            # Create empty file with header
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Path', 'Total Bytes', 'Used Bytes', 'Free Bytes',
                               'Percent Used', 'Percent Free'])
            return filepath

        # Get all unique paths from the data
        paths = set()
        for data_point in historical_data:
            for key in data_point.keys():
                if not key.startswith('_') and key not in ['timestamp', 'generated_at']:
                    paths.add(key)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Timestamp', 'Path', 'Total Bytes', 'Used Bytes', 'Free Bytes',
                           'Percent Used', 'Percent Free'])

            # Write data rows
            for data_point in historical_data:
                timestamp = data_point.get('timestamp', data_point.get('generated_at', ''))
                for path in paths:
                    if path in data_point:
                        info = data_point[path]
                        writer.writerow([
                            timestamp,
                            path,
                            info.get('total_bytes', 0),
                            info.get('used_bytes', 0),
                            info.get('free_bytes', 0),
                            info.get('percent_used', 0),
                            info.get('percent_free', 0)
                        ])

        self.logger.info(f"CSV trend report generated: {filepath}")
        return filepath

    def _generate_text_trend_report(self, historical_data: List[Dict[str, Any]], filepath: str) -> str:
        """Generate text format trend report."""
        with open(filepath, 'w') as f:
            f.write("DISK USAGE TREND REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Points: {len(historical_data)}\n\n")

            if not historical_data:
                f.write("No historical data available.\n")
                return filepath

            # Get all unique paths
            paths = set()
            for data_point in historical_data:
                for key in data_point.keys():
                    if not key.startswith('_') and key not in ['timestamp', 'generated_at']:
                        paths.add(key)

            for path in sorted(paths):
                f.write(f"Path: {path}\n")
                f.write("-" * 30 + "\n")

                # Find data points for this path
                path_data = []
                for data_point in historical_data:
                    if path in data_point:
                        path_data.append({
                            'timestamp': data_point.get('timestamp', data_point.get('generated_at', '')),
                            'percent_used': data_point[path].get('percent_used', 0)
                        })

                if path_data:
                    f.write(f"{'Timestamp':<20} {'Usage (%)':<10}\n")
                    f.write("-" * 30 + "\n")
                    for data_point in path_data[-10:]:  # Show last 10 entries
                        ts = data_point['timestamp']
                        if ts:
                            try:
                                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                formatted_time = dt.strftime('%m/%d %H:%M')
                            except:
                                formatted_time = ts[:16] if len(ts) > 16 else ts
                        else:
                            formatted_time = "Unknown"
                        f.write(f"{formatted_time:<20} {data_point['percent_used']:<10.1f}\n")
                else:
                    f.write("No data available for this path.\n")

                f.write("\n")

        self.logger.info(f"Text trend report generated: {filepath}")
        return filepath

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

    def list_reports(self) -> List[str]:
        """
        List all generated reports.

        Returns:
            List of report file paths
        """
        reports = []
        if os.path.exists(self.reports_dir):
            for filename in os.listdir(self.reports_dir):
                if filename.endswith(('.json', '.csv', '.txt')):
                    reports.append(os.path.join(self.reports_dir, filename))
        return sorted(reports, key=os.path.getmtime, reverse=True)

    def cleanup_old_reports(self, days_to_keep: int = 30):
        """
        Clean up old report files.

        Args:
            days_to_keep: Number of days to keep reports
        """
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        removed_count = 0

        if os.path.exists(self.reports_dir):
            for filename in os.listdir(self.reports_dir):
                filepath = os.path.join(self.reports_dir, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff_time:
                        try:
                            os.remove(filepath)
                            removed_count += 1
                        except OSError as e:
                            self.logger.warning(f"Could not remove old report {filepath}: {e}")

        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old report files")