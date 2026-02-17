# Grok Nightly X Scan

This directory contains the nightly scanning infrastructure for Grok. It scans X (Twitter) for high-relevance content related to BPR&D projects and research topics, generating daily reports and morning briefing handoffs.

## Setup

1.  **Dependencies:**
    *   `tweepy` (optional, for real API access)
    *   Standard Python 3 libraries

2.  **Environment Variables:**
    *   `X_BEARER_TOKEN`: Required for real API access. If missing, the script runs in **Mock Mode** using `mock_x_data.json`.

## Usage

Run the script manually:
```bash
python3 research/grok-nightly/x_nightly_scan.py
```

## Scheduling

### GitHub Actions (Example)
Create `.github/workflows/grok-nightly-scan.yml`:

```yaml
name: Grok Nightly X Scan

on:
  schedule:
    - cron: "0 8 * * *"  # Runs at 08:00 UTC (00:00 PST)
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Dependencies
        run: |
          pip install tweepy

      - name: Run Scan
        env:
          X_BEARER_TOKEN: ${{ secrets.X_BEARER_TOKEN }}
        run: python3 research/grok-nightly/x_nightly_scan.py

      - name: Commit Results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add research/grok-nightly/*.md research/grok-nightly/*.json _agents/_handoffs/*.md
          git commit -m "Grok Nightly Scan: $(date +%Y-%m-%d)" || true
          git push
```

### Render Cron Job (Example)
Add to your `render.yaml`:

```yaml
services:
  - type: cron
    name: grok-nightly-scan
    env: python
    schedule: "0 8 * * *" # 08:00 UTC
    buildCommand: "pip install tweepy"
    startCommand: "python3 research/grok-nightly/x_nightly_scan.py"
    envVars:
      - key: X_BEARER_TOKEN
        sync: false
```

## Prototype Limitations
*   **Query Construction:** Currently, the script constructs a query using only the top 3 loaded keywords to avoid hitting API character limits on the Basic tier. In production, this should be upgraded to use query pagination or a more sophisticated query builder.
*   **Mock Data:** The mock mode uses a static JSON file (`mock_x_data.json`).
