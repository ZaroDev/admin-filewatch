"""
Setup script for Disk Usage Monitor Application
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="disk-usage-monitor",
    version="1.0.0",
    author="Disk Usage Monitor Team",
    author_email="admin@example.com",
    description="A disk usage monitoring application with email alerts and reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/disk-usage-monitor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Add any required packages here
        # For basic functionality, we only use standard library
        # If we add psutil for better disk monitoring, uncomment below:
        # "psutil>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "disk-monitor=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)