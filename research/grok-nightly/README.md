# Grok Nightly X Scan – Trial v0.1

This directory contains the nightly scanning infrastructure for Grok. It scans X (Twitter) for high-relevance content related to BPR&D projects and research topics, generating daily reports and morning briefing handoffs.

## Setup

1.  **Dependencies:**
    *   `tweepy` (Required for real data)
    *   `abacusai` (Optional, for LLM scoring)

2.  **Environment Variables:**
    *   `X_BEARER_TOKEN`: **Required**. If missing, the script generates a "Trial Run Skipped" report and exits.
    *   `ABACUS_PRIMARY_KEY`: Optional. Used for relevance scoring.

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
          pip install tweepy abacusai

      - name: Run Scan
        env:
          X_BEARER_TOKEN: ${{ secrets.X_BEARER_TOKEN }}
          ABACUS_PRIMARY_KEY: ${{ secrets.ABACUS_PRIMARY_KEY }}
        run: python3 research/grok-nightly/x_nightly_scan.py

      - name: Commit Results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add research/grok-nightly/*.md _agents/_handoffs/*.md
          git commit -m "Grok Nightly Scan: $(date +%Y-%m-%d)" || true
          git push
```

## Limitations (v0.1)
*   **Query Construction:** Uses keyword chunking to stay within Basic tier limits.
*   **Scoring:** Falls back to keyword matching if Abacus LLM is unavailable.
