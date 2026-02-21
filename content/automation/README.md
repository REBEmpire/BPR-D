# Content Automation

This directory contains tools for automating content generation and publishing to Hive.

## Components
- `orchestrator.py`: Main controller for multi-account publishing.
- `content_generator.py`: AI-powered content creation (Claude, OpenAI).
- `hive_publisher.py`: Hive blockchain interaction.
- `tests/`: Unit tests.

## Testing
To run tests:
```bash
python3 -m unittest discover content/automation/tests
```

## Hive Pipeline MVP
The current MVP pipeline is located at `pipelines/content/hive-pipeline-v0.1.py`. It converts Daily Briefs into Hive drafts.

Usage:
```bash
python3 pipelines/content/hive-pipeline-v0.1.py --input research/daily_briefs/latest.md --mock
```
