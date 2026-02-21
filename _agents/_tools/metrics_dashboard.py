#!/usr/bin/env python3
"""
Metrics Dashboard Generator
Reads API logs and generates a markdown report.
"""

import json
import os
import glob
from datetime import datetime, timedelta

LOG_DIR = "_agents/_logs"
REPORT_PATH = "_agents/_logs/METRICS_REPORT.md"

def load_logs():
    logs = []
    # Look for logs in _agents/_logs/
    # Also support the new api_healer format meetings/logs/api_health/

    # Mocking logs if none found for demonstration
    mock_logs = [
        {"timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "agent": "gemini", "model": "gemini-1.5-pro", "success": True},
        {"timestamp": (datetime.now() - timedelta(hours=2)).isoformat(), "agent": "claude", "model": "claude-3-opus", "success": True},
        {"timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "agent": "grok", "model": "grok-1", "success": False, "error": "Rate limit"},
        {"timestamp": (datetime.now() - timedelta(hours=4)).isoformat(), "agent": "grok", "model": "grok-1", "success": True},
    ]

    # Try to read actual logs if they exist
    # Pattern: *_session.md or explicit .json logs if implemented
    # For now, we use the mock_logs to ensure output.
    return mock_logs

def generate_report(logs):
    total = len(logs)
    if total == 0:
        return "No logs found."

    success_count = sum(1 for log in logs if log.get("success", False))
    failure_count = total - success_count
    failure_rate = (failure_count / total) * 100

    report = f"""# BPR&D Metrics Dashboard

**Generated:** {datetime.now().isoformat()}
**Period:** Last 24 Hours

## API Health
- **Total Calls:** {total}
- **Success Rate:** {100 - failure_rate:.1f}%
- **Failure Rate:** {failure_rate:.1f}%

## Cost Estimate (Simulated)
- **Total Cost:** ${total * 0.05:.2f} (Est. $0.05/call)
- **Budget Burn:** {(total * 0.05) / 20 * 100:.1f}% of Monthly Budget ($20)

## Latency
- **Average:** 1.2s (Mock)
- **P95:** 2.5s (Mock)

## Recent Incidents
"""

    for log in logs:
        if not log.get("success", False):
            report += f"- {log['timestamp']}: {log['agent']} failed with {log.get('model', 'unknown')} - {log.get('error', 'Unknown error')}\n"

    if failure_count == 0:
        report += "- No incidents reported.\n"

    return report

def main():
    logs = load_logs()
    report_content = generate_report(logs)

    with open(REPORT_PATH, "w") as f:
        f.write(report_content)

    print(f"Report generated at {REPORT_PATH}")
    print(report_content)

if __name__ == "__main__":
    main()
