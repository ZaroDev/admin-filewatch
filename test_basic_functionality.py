#!/usr/bin/env python3
"""
Basic functionality test for Disk Usage Monitor Application
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from config_manager import ConfigManager
        from logger import Logger
        from disk_monitor import DiskMonitor
        from email_notifier import EmailNotifier
        from alert_manager import AlertManager
        from space_analyzer import SpaceAnalyzer
        from report_generator import ReportGenerator
        from graph_visualizer import GraphVisualizer
        from web_dashboard import WebDashboard
        print("+ All modules imported successfully")
        return True
    except Exception as e:
        print("x Import error: {e}")
        return False

def test_config_manager():
    """Test configuration manager."""
    try:
        from config_manager import ConfigManager
        config = ConfigManager()
        config.load_config()
        disk_config = config.get_disk_monitor_config()
        assert 'paths_to_monitor' in disk_config
        assert 'check_interval_seconds' in disk_config
        print("+ Configuration manager works")
        return True
    except Exception as e:
        print(f"x Configuration manager error: {e}")
        return False

def test_disk_monitor():
    """Test disk monitor."""
    try:
        from logger import Logger
        from disk_monitor import DiskMonitor
        logger = Logger({'level': 'INFO', 'console_output': False, 'file_path': ''})
        config = {'paths_to_monitor': ['C:'], 'check_interval_seconds': 300}
        monitor = DiskMonitor(config, logger)
        info = monitor.get_disk_usage('C:')
        assert 'percent_used' in info
        assert 'total_bytes' in info
        assert info['total_bytes'] > 0
        print("+ Disk monitor works")
        return True
    except Exception as e:
        print(f"x Disk monitor error: {e}")
        return False

def test_space_analyzer():
    """Test space analyzer on a small directory."""
    try:
        from logger import Logger
        from space_analyzer import SpaceAnalyzer
        logger = Logger({'level': 'INFO', 'console_output': False, 'file_path': ''})
        config = {
            'scan_depth': 1,
            'min_file_size_mb': 0.001,  # Very small for testing
            'exclude_paths': [],
            'exclude_file_patterns': []
        }
        analyzer = SpaceAnalyzer(config, logger)
        # Test on current directory
        result = analyzer.analyze_path('.')
        assert 'large_files' in result
        assert 'large_folders' in result
        print("+ Space analyzer works")
        return True
    except Exception as e:
        print(f"x Space analyzer error: {e}")
        return False

def test_report_generator():
    """Test report generator."""
    try:
        from logger import Logger
        from report_generator import ReportGenerator
        logger = Logger({'level': 'INFO', 'console_output': False, 'file_path': ''})
        reporter = ReportGenerator(logger)

        # Test data
        disk_info = {
            'C:': {
                'total_bytes': 1000000000,
                'used_bytes': 500000000,
                'free_bytes': 500000000,
                'percent_used': 50.0,
                'percent_free': 50.0
            }
        }

        report_path = reporter.generate_disk_usage_report(disk_info, 'json')
        assert os.path.exists(report_path)
        print("+ Report generator works")
        return True
    except Exception as e:
        print(f"x Report generator error: {e}")
        return False

def main():
    """Run all tests."""
    print("Running basic functionality tests...\n")

    tests = [
        test_imports,
        test_config_manager,
        test_disk_monitor,
        test_space_analyzer,
        test_report_generator
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("! All tests passed!")
        return 0
    else:
        print("x Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())