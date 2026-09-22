"""
Web Dashboard module for Disk Usage Monitor Application
Provides a web-based interface for viewing disk status, reports, and graphs.
"""

import threading
import time
import webbrowser
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs


class WebDashboard:
    def __init__(self, config: Dict[str, Any], disk_monitor, alert_manager, logger):
        """
        Initialize the web dashboard.

        Args:
            config: Web dashboard configuration dictionary
            disk_monitor: DiskMonitor instance
            alert_manager: AlertManager instance
            logger: Logger instance
        """
        self.config = config
        self.disk_monitor = disk_monitor
        self.alert_manager = alert_manager
        self.logger = logger
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 5000)
        self.debug = config.get('debug', False)
        self.server = None
        self.server_thread = None
        self.running = False
        self.latest_disk_info = {}
        self.latest_analysis_info = {}
        self.historical_data = []  # Store historical disk usage data
        self.max_history_points = 100  # Keep last 100 data points

        # Import graph visualizer
        from graph_visualizer import GraphVisualizer
        self.graph_visualizer = GraphVisualizer(logger)

        # Import report generator
        from report_generator import ReportGenerator
        self.report_generator = ReportGenerator(logger)

    def start(self):
        """Start the web dashboard server."""
        if self.running:
            self.logger.warning("Web dashboard is already running")
            return

        try:
            self.server = HTTPServer((self.host, self.port), self._create_handler())
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.running = True

            # Try to open browser automatically
            try:
                webbrowser.open(f'http://{self.host}:{self.port}')
            except:
                pass  # Ignore if browser can't be opened

            self.logger.info(f"Web dashboard started at http://{self.host}:{self.port}")

        except Exception as e:
            self.logger.error(f"Failed to start web dashboard: {e}")
            self.running = False

    def stop(self):
        """Stop the web dashboard server."""
        if not self.running:
            self.logger.warning("Web dashboard is not running")
            return

        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        if self.server_thread:
            self.server_thread.join(timeout=5)

        self.logger.info("Web dashboard stopped")

    def _run_server(self):
        """Run the HTTP server."""
        try:
            self.logger.info(f"Starting web server on {self.host}:{self.port}")
            self.server.serve_forever()
        except Exception as e:
            if self.running:  # Only log error if we're still supposed to be running
                self.logger.error(f"Web server error: {e}")
        finally:
            self.running = False

    def _create_handler(self):
        """Create a request handler class with access to dashboard instance."""
        dashboard = self

        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                """Handle GET requests."""
                parsed_path = urlparse(self.path)
                path = parsed_path.path
                query_params = parse_qs(parsed_path.query)

                try:
                    if path == '/' or path == '/index.html':
                        self._serve_dashboard()
                    elif path == '/api/disk-info':
                        self._serve_disk_info()
                    elif path == '/api/analysis':
                        self._serve_analysis()
                    elif path == '/api/history':
                        self._serve_history()
                    elif path == '/api/reports':
                        self._serve_reports()
                    elif path == '/api/alerts':
                        self._serve_alerts()
                    elif path.startswith('/static/'):
                        self._serve_static_file(path)
                    else:
                        self._serve_404()
                except Exception as e:
                    dashboard.logger.error(f"Error handling request {path}: {e}")
                    self._serve_500(str(e))

            def do_POST(self):
                """Handle POST requests."""
                parsed_path = urlparse(self.path)
                path = parsed_path.path

                try:
                    if path == '/api/analyze':
                        self._handle_analyze_request()
                    else:
                        self._serve_404()
                except Exception as e:
                    dashboard.logger.error(f"Error handling POST request {path}: {e}")
                    self._serve_500(str(e))

            def _serve_dashboard(self):
                """Serve the main dashboard HTML page."""
                try:
                    # Get latest data
                    disk_info = dashboard.latest_disk_info or dashboard.disk_monitor.check_all_paths()

                    # Generate HTML dashboard
                    html_content = dashboard.graph_visualizer.generate_html_dashboard(
                        disk_info,
                        dashboard.latest_analysis_info,
                        dashboard.historical_data
                    )

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error serving dashboard: {e}")
                    self._serve_500(str(e))

            def _serve_disk_info(self):
                """Serve current disk info as JSON."""
                try:
                    # Update latest data
                    disk_info = dashboard.disk_monitor.check_all_paths()
                    dashboard.latest_disk_info = disk_info

                    # Add to historical data (keep limited history)
                    history_entry = {
                        'timestamp': disk_info.get('_summary', {}).get('timestamp'),
                        'generated_at': dashboard._get_current_timestamp()
                    }
                    # Add each path's data
                    for path, info in disk_info.items():
                        if not path.startswith('_') and 'error' not in info:
                            history_entry[path] = info

                    dashboard.historical_data.append(history_entry)
                    if len(dashboard.historical_data) > dashboard.max_history_points:
                        dashboard.historical_data = dashboard.historical_data[-dashboard.max_history_points:]

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(disk_info, indent=2).encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error serving disk info: {e}")
                    self._serve_500(str(e))

            def _serve_analysis(self):
                """Serve space analysis data as JSON."""
                try:
                    # If we don't have recent analysis, run a quick scan on primary path
                    if not dashboard.latest_analysis_info:
                        disk_config = dashboard.config.get('disk_monitor', {})
                        paths = disk_config.get('paths_to_monitor', ['C:'])
                        if paths:
                            from space_analyzer import SpaceAnalyzer
                            analyzer = SpaceAnalyzer(
                                dashboard.config.get('space_analyzer', {}),
                                dashboard.logger
                            )
                            dashboard.latest_analysis_info = analyzer.analyze_path(paths[0])

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(dashboard.latest_analysis_info, indent=2).encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error serving analysis: {e}")
                    self._serve_500(str(e))

            def _serve_history(self):
                """Serve historical data as JSON."""
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(dashboard.historical_data, indent=2).encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error serving history: {e}")
                    self._serve_500(str(e))

            def _serve_reports(self):
                """Serve list of available reports."""
                try:
                    reports = dashboard.report_generator.list_reports()
                    report_list = []
                    for report in reports:
                        stat = os.stat(report)
                        report_list.append({
                            'filename': os.path.basename(report),
                            'path': report,
                            'size': stat.st_size,
                            'modified': stat.st_mtime
                        })

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(report_list, indent=2).encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error serving reports: {e}")
                    self._serve_500(str(e))

            def _serve_alerts(self):
                """Serve alert history as JSON."""
                try:
                    alerts = {
                        'alert_history': dashboard.alert_manager.alert_history,
                        'thresholds': {
                            'warning': dashboard.alert_manager.warning_threshold,
                            'critical': dashboard.alert_manager.critical_threshold,
                            'emergency': dashboard.alert_manager.emergency_threshold
                        }
                    }

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(alerts, indent=2).encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error serving alerts: {e}")
                    self._serve_500(str(e))

            def _handle_analyze_request(self):
                """Handle request to run space analysis."""
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        path = data.get('path', 'C:')
                    else:
                        # Default to first monitored path
                        disk_config = dashboard.config.get('disk_monitor', {})
                        paths = disk_config.get('paths_to_monitor', ['C:'])
                        path = paths[0] if paths else 'C:'

                    # Run analysis
                    from space_analyzer import SpaceAnalyzer
                    analyzer = SpaceAnalyzer(
                        dashboard.config.get('space_analyzer', {}),
                        dashboard.logger
                    )
                    analysis_result = analyzer.analyze_path(path)
                    dashboard.latest_analysis_info = analysis_result

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(analysis_result, indent=2).encode('utf-8'))
                except Exception as e:
                    dashboard.logger.error(f"Error handling analyze request: {e}")
                    self._serve_500(str(e))

            def _serve_static_file(self, path):
                """Serve static files (CSS, JS, etc.)."""
                try:
                    # Remove leading slash and static prefix
                    file_path = path[1:]  # Remove leading /

                    # Security check: prevent directory traversal
                    if '..' in file_path or file_path.startswith('/'):
                        self._serve_403()
                        return

                    # For now, we'll serve simple static content or return 404
                    # In a full implementation, we'd serve actual static files
                    self._serve_404()
                except Exception as e:
                    dashboard.logger.error(f"Error serving static file {path}: {e}")
                    self._serve_500(str(e))

            def _serve_404(self):
                """Serve 404 Not Found."""
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 Not Found</h1><p>The requested resource was not found.</p>')

            def _serve_403(self):
                """Serve 403 Forbidden."""
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>403 Forbidden</h1><p>Access to this resource is forbidden.</p>')

            def _serve_500(self, error_msg: str):
                """Serve 500 Internal Server Error."""
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'<h1>500 Internal Server Error</h1><p>{error_msg}</p>'.encode('utf-8'))

            def log_message(self, format, *args):
                """Override to use our logger instead of stderr."""
                if dashboard.debug:
                    dashboard.logger.debug(f"{self.address_string()} - {format % args}")
                # Otherwise don't log to keep console clean

        return DashboardHandler

    def update_disk_info(self, disk_info: Dict[str, Any]):
        """
        Update the latest disk information.

        Args:
            disk_info: Disk usage information from disk monitor
        """
        self.latest_disk_info = disk_info

        # Add to historical data
        history_entry = {
            'timestamp': disk_info.get('_summary', {}).get('timestamp'),
            'generated_at': self._get_current_timestamp()
        }
        # Add each path's data
        for path, info in disk_info.items():
            if not path.startswith('_') and 'error' not in info:
                history_entry[path] = info

        self.historical_data.append(history_entry)
        if len(self.historical_data) > self.max_history_points:
            self.historical_data = self.historical_data[-self.max_history_points:]

    def update_analysis_info(self, analysis_info: Dict[str, Any]):
        """
        Update the latest analysis information.

        Args:
            analysis_info: Space analysis information
        """
        self.latest_analysis_info = analysis_info

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()