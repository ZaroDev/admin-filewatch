"""
Graph Visualizer module for Disk Usage Monitor Application
Creates simple visualizations of disk usage data.
"""

import os
from typing import Dict, List, Any
from datetime import datetime, timedelta


class GraphVisualizer:
    def __init__(self, logger):
        """
        Initialize the graph visualizer.

        Args:
            logger: Logger instance
        """
        self.logger = logger

    def create_usage_bar_chart(self, disk_info: Dict[str, Any], width: int = 50) -> str:
        """
        Create a simple text-based bar chart showing disk usage percentages.

        Args:
            disk_info: Disk usage information from disk monitor
            width: Width of the bar chart in characters

        Returns:
            String containing the bar chart
        """
        output = []
        output.append("DISK USAGE BAR CHART")
        output.append("=" * (width + 20))
        output.append("")

        # Filter out summary and error entries
        paths_data = {}
        for path, info in disk_info.items():
            if not path.startswith('_') and 'error' not in info:
                paths_data[path] = info.get('percent_used', 0)

        if not paths_data:
            output.append("No disk usage data available")
            return "\n".join(output)

        # Find maximum usage for scaling
        max_usage = max(paths_data.values()) if paths_data else 100
        scale_factor = width / max(max_usage, 1)  # Avoid division by zero

        for path, usage_percent in sorted(paths_data.items(), key=lambda x: x[1], reverse=True):
            bar_length = int(usage_percent * scale_factor)
            bar = "█" * bar_length + "░" * (width - bar_length)

            # Color coding based on usage (using text symbols since we can't use actual colors in all terminals)
            if usage_percent >= 90:
                indicator = "!!!"
            elif usage_percent >= 80:
                indicator = "!!"
            elif usage_percent >= 70:
                indicator = "!"
            else:
                indicator = ""

            output.append(f"{path:<20} [{bar}] {usage_percent:5.1f}% {indicator}")

        output.append("")
        output.append("Legend: !!! Critical (>90%) !! Warning (>80%) ! Elevated (>70%)")
        output.append("        █ Used Space   ░ Free Space")

        return "\n".join(output)

    def create_usage_pie_chart(self, disk_info: Dict[str, Any]) -> List[str]:
        """
        Create a simple text-based pie chart representation.

        Args:
            disk_info: Disk usage information from disk monitor

        Returns:
            List of strings representing the pie chart
        """
        output = []
        output.append("DISK USAGE DISTRIBUTION")
        output.append("=" * 30)
        output.append("")

        # For simplicity, we'll show the most used path
        paths_data = {}
        for path, info in disk_info.items():
            if not path.startswith('_') and 'error' not in info:
                paths_data[path] = info.get('percent_used', 0)

        if not paths_data:
            output.append("No disk usage data available")
            return output

        # Find the path with highest usage
        if paths_data:
            max_path, max_usage = max(paths_data.items(), key=lambda x: x[1])

            # Simple pie chart approximation using characters
            total_chars = 40
            used_chars = int((max_usage / 100) * total_chars)
            free_chars = total_chars - used_chars

            # Create pie chart rows
            for i in range(total_chars // 2):  # Top half
                if i < used_chars // 2:
                    output.append("█" * total_chars)
                elif i < total_chars // 2:
                    output.append("░" * total_chars)
                else:
                    output.append(" " * total_chars)

            output.append(f" {max_path}: {max_usage:.1f}% used")
            output.append("")
            output.append("█ Used Space   ░ Free Space")

        return output

    def create_trend_sparkline(self, usage_history: List[float], width: int = 50) -> str:
        """
        Create a sparkline showing usage trend over time.

        Args:
            usage_history: List of usage percentages over time
            width: Width of the sparkline

        Returns:
            String representing the sparkline
        """
        if len(usage_history) < 2:
            return "Insufficient data for trend"

        # Normalize data to 0-1 range
        min_val = min(usage_history)
        max_val = max(usage_history)
        range_val = max_val - min_val

        if range_val == 0:
            normalized = [0.5] * len(usage_history)  # All same value
        else:
            normalized = [(x - min_val) / range_val for x in usage_history]

        # Sample data to fit width
        if len(normalized) > width:
            step = len(normalized) / width
            sampled = [normalized[int(i * step)] for i in range(width)]
        else:
            sampled = normalized
            # Pad if needed
            while len(sampled) < width:
                sampled.append(sampled[-1] if sampled else 0)

        # Sparkline characters (from lowest to highest)
        sparkline_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        # Create sparkline
        sparkline = ""
        for val in sampled:
            char_index = int(val * (len(sparkline_chars) - 1))
            sparkline += sparkline_chars[char_index]

        # Add labels
        current = usage_history[-1] if usage_history else 0
        minimum = min(usage_history)
        maximum = max(usage_history)

        result = f"Usage Trend: {sparkline}\n"
        result += f"Current: {current:.1f}%  Min: {minimum:.1f}%  Max: {maximum:.1f}%"

        return result

    def generate_html_dashboard(self, disk_info: Dict[str, Any],
                              analysis_info: Dict[str, Any] = None,
                              historical_data: List[Dict[str, Any]] = None) -> str:
        """
        Generate a simple HTML dashboard.

        Args:
            disk_info: Current disk usage information
            analysis_info: Space analysis information (optional)
            historical_data: Historical usage data (optional)

        Returns:
            HTML string for the dashboard
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Disk Usage Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1, h2 {{ color: #333; }}
        .disk-card {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
        .usage-bar {{ height: 20px; background-color: #eee; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
        .usage-fill {{ height: 100%; background-color: #4CAF50; transition: width 0.3s; }}
        .usage-fill.warning {{ background-color: #ff9800; }}
        .usage-fill.critical {{ background-color: #f44336; }}
        .usage-fill.emergency {{ background-color: #d32f2f; }}
        .stats {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 15px 0; }}
        .stat-item {{ flex: 1; min-width: 150px; }}
        .stat-label {{ font-size: 0.9em; color: #666; }}
        .stat-value {{ font-size: 1.2em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .refresh-btn {{ background-color: #2196F3; color: white; border: none; padding: 10px 20px;
                       border-radius: 5px; cursor: pointer; }}
        .refresh-btn:hover {{ background-color: #0b7dda; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Disk Usage Monitor</h1>
        <div class="timestamp">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <button class="refresh-btn" onclick="location.reload()">Refresh Data</button>

        <h2>Disk Usage Overview</h2>
        <div class="stats">
"""

        # Add disk usage cards
        for path, info in disk_info.items():
            if path.startswith('_') or 'error' in info:
                continue

            usage_percent = info.get('percent_used', 0)
            # Determine status class
            if usage_percent >= 90:
                status_class = "emergency"
            elif usage_percent >= 80:
                status_class = "critical"
            elif usage_percent >= 70:
                status_class = "warning"
            else:
                status_class = ""

            html += f"""
            <div class="disk-card">
                <h3>{path}</h3>
                <div class="usage-bar">
                    <div class="usage-fill {status_class}" style="width: {usage_percent}%"></div>
                </div>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-label">Usage</div>
                        <div class="stat-value">{usage_percent:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Used</div>
                        <div class="stat-value">{self._format_bytes(info.get('used_bytes', 0))}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Free</div>
                        <div class="stat-value">{self._format_bytes(info.get('free_bytes', 0))}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total</div>
                        <div class="stat-value">{self._format_bytes(info.get('total_bytes', 0))}</div>
                    </div>
                </div>
            </div>
"""

        html += """
        </div>

        <h2>Space Analysis</h2>
"""

        # Add space analysis if available
        if analysis_info and 'large_files' in analysis_info:
            html += """
        <h3>Largest Files</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>File Path</th>
                    <th>Size</th>
                    <th>Modified</th>
                </tr>
            </thead>
            <tbody>
"""

            for i, file_info in enumerate(analysis_info['large_files'][:10], 1):  # Top 10
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{file_info.get('path', 'Unknown')}</td>
                    <td>{self._format_bytes(file_info.get('size_bytes', 0))}</td>
                    <td>{datetime.fromtimestamp(file_info.get('modified_time', 0)).strftime('%Y-%m-%d %H:%M') if file_info.get('modified_time') else 'Unknown'}</td>
                </tr>
"""

            html += """
            </tbody>
        </table>
"""

            if analysis_info.get('large_folders'):
                html += """
        <h3>Largest Folders</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Folder Path</th>
                    <th>Size</th>
                    <th>Files</th>
                </tr>
            </thead>
            <tbody>
"""

                for i, folder_info in enumerate(analysis_info['large_folders'][:10], 1):  # Top 10
                    html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{folder_info.get('path', 'Unknown')}</td>
                        <td>{self._format_bytes(folder_info.get('size_bytes', 0))}</td>
                        <td>{folder_info.get('file_count', 0)}</td>
                    </tr>
"""

                html += """
            </tbody>
        </table>
"""

        html += """
    </div>

    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function() {
            location.reload();
        }, 300000);
    </script>
</body>
</html>
"""

        return html

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