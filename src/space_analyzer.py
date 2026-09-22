"""
Space Analyzer module for Disk Usage Monitor Application
Analyzes disk usage to identify large files and folders consuming storage.
"""

import os
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path


class SpaceAnalyzer:
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the space analyzer.

        Args:
            config: Space analyzer configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.scan_depth = config.get('scan_depth', 3)
        self.min_file_size_mb = config.get('min_file_size_mb', 10)
        self.exclude_paths = config.get('exclude_paths', [])
        self.exclude_file_patterns = config.get('exclude_file_patterns', [])

        # Convert MB to bytes for comparison
        self.min_file_size_bytes = self.min_file_size_mb * 1024 * 1024

    def analyze_path(self, path: str) -> Dict[str, Any]:
        """
        Analyze a path to find large files and folders.

        Args:
            path: Path to analyze

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Handle Windows drive letters
            if len(path) == 2 and path.endswith(':'):
                path = path + '\\'

            if not os.path.exists(path):
                return {
                    'path': path,
                    'error': f'Path does not exist: {path}',
                    'large_files': [],
                    'large_folders': [],
                    'scan_time': 0
                }

            start_time = time.time()

            # Scan for large files
            large_files = self._scan_for_large_files(path)

            # Scan for large folders
            large_folders = self._scan_for_large_folders(path)

            scan_time = time.time() - start_time

            return {
                'path': path,
                'large_files': large_files,
                'large_folders': large_folders,
                'scan_time': round(scan_time, 2),
                'total_large_files': len(large_files),
                'total_large_folders': len(large_folders)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing path {path}: {e}")
            return {
                'path': path,
                'error': str(e),
                'large_files': [],
                'large_folders': [],
                'scan_time': 0
            }

    def _scan_for_large_files(self, root_path: str) -> List[Dict[str, Any]]:
        """
        Scan for large files in the given path.

        Args:
            root_path: Root path to scan

        Returns:
            List of dictionaries containing file information
        """
        large_files = []

        try:
            for root, dirs, files in os.walk(root_path):
                # Modify dirs in-place to exclude unwanted directories
                dirs[:] = [d for d in dirs if not self._should_exclude_path(os.path.join(root, d))]

                # Check current depth
                depth = root[len(root_path):].count(os.sep)
                if depth >= self.scan_depth:
                    # Don't go deeper than specified depth
                    dirs[:] = []

                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip if file matches exclude patterns
                    if self._should_exclude_file(file_path):
                        continue

                    try:
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)

                            # Only include files larger than minimum size
                            if file_size >= self.min_file_size_bytes:
                                large_files.append({
                                    'path': file_path,
                                    'size_bytes': file_size,
                                    'size_human': self._format_bytes(file_size),
                                    'modified_time': os.path.getmtime(file_path)
                                })
                    except (OSError, IOError) as e:
                        # Skip files we can't access
                        self.logger.debug(f"Could not access file {file_path}: {e}")
                        continue

            # Sort by size (largest first)
            large_files.sort(key=lambda x: x['size_bytes'], reverse=True)

            # Limit results to top 20 to avoid overwhelming output
            return large_files[:20]

        except Exception as e:
            self.logger.error(f"Error scanning for large files in {root_path}: {e}")
            return []

    def _scan_for_large_folders(self, root_path: str) -> List[Dict[str, Any]]:
        """
        Scan for large folders in the given path.

        Args:
            root_path: Root path to scan

        Returns:
            List of dictionaries containing folder information
        """
        folder_sizes = {}

        try:
            # First pass: calculate sizes of all folders
            for root, dirs, files in os.walk(root_path):
                # Modify dirs in-place to exclude unwanted directories
                dirs[:] = [d for d in dirs if not self._should_exclude_path(os.path.join(root, d))]

                # Check current depth
                depth = root[len(root_path):].count(os.sep)
                if depth >= self.scan_depth:
                    # Don't go deeper than specified depth
                    dirs[:] = []

                folder_size = 0
                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip if file matches exclude patterns
                    if self._should_exclude_file(file_path):
                        continue

                    try:
                        if os.path.isfile(file_path):
                            folder_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        # Skip files we can't access
                        continue

                folder_sizes[root] = folder_size

            # Convert to list and filter by minimum size
            large_folders = []
            for folder_path, size_bytes in folder_sizes.items():
                if size_bytes >= self.min_file_size_bytes:
                    large_folders.append({
                        'path': folder_path,
                        'size_bytes': size_bytes,
                        'size_human': self._format_bytes(size_bytes),
                        'file_count': self._count_files_in_folder(folder_path)
                    })

            # Sort by size (largest first)
            large_folders.sort(key=lambda x: x['size_bytes'], reverse=True)

            # Limit results to top 20
            return large_folders[:20]

        except Exception as e:
            self.logger.error(f"Error scanning for large folders in {root_path}: {e}")
            return []

    def _should_exclude_path(self, path: str) -> bool:
        """
        Check if a path should be excluded from scanning.

        Args:
            path: Path to check

        Returns:
            True if path should be excluded, False otherwise
        """
        path_lower = path.lower()
        for exclude_pattern in self.exclude_paths:
            if exclude_pattern.lower() in path_lower:
                return True
        return False

    def _should_exclude_file(self, file_path: str) -> bool:
        """
        Check if a file should be excluded from scanning.

        Args:
            file_path: File path to check

        Returns:
            True if file should be excluded, False otherwise
        """
        file_name = os.path.basename(file_path).lower()
        for pattern in self.exclude_file_patterns:
            # Simple wildcard matching
            if pattern.startswith('*.') and file_name.endswith(pattern[1:]):
                return True
            elif pattern in file_name:
                return True
        return False

    def _count_files_in_folder(self, folder_path: str) -> int:
        """
        Count the number of files in a folder (non-recursive).

        Args:
            folder_path: Path to folder

        Returns:
            Number of files in the folder
        """
        try:
            count = 0
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path) and not self._should_exclude_file(item_path):
                    count += 1
            return count
        except (OSError, IOError):
            return 0

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