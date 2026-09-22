# Disk Usage Monitor Application

A disk usage monitoring application that tracks storage utilization, sends email alerts when disk space is low, provides visual reports and graphs, and includes extensible notification mechanisms.

## Features

- Monitors disk space usage on specified drives/paths
- Sends email alerts when disk usage exceeds configurable thresholds
- Provides web-based dashboard for real-time status and reports
- Analyzes disk space to identify large files and folders
- Extensible notification system (easy to add SMS, Slack, webhook, etc.)
- Comprehensive logging and error handling
- Configurable via JSON file

## Installation

1. Clone the repository
2. Install dependencies (if any)
3. Configure the application in `config/config.json`
4. Run the application

## Configuration

Edit `config/config.json` to adjust:

- Disk monitoring paths and intervals
- Alert thresholds (warning, critical, emergency)
- Email notification settings
- Logging preferences
- Web dashboard settings
- Space analysis configuration

## Usage

Run the main application:
```
python src/main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License

Copyright (c) [2026] [Zarodev]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.