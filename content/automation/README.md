# DDAS Content Automation Pipeline

**Assigned Agent:** Gemini
**Status:** MVP

## Overview
This pipeline automates the generation and publishing of content for the DDAS ecosystem on the Hive blockchain. It manages 5 distinct accounts (Dev Blog, Lore, Strategy, Community, News) and uses AI to generate content.

## Components
-   `orchestrator.py`: Main entry point. Manages the daily cycle.
-   `content_generator.py`: Interfaces with AI providers (Claude, OpenAI, etc.) to generate content.
-   `hive_publisher.py`: Handles Hive blockchain interactions (posting, scheduling).

## Setup
1.  **Dependencies:**
    -   `pip install beespy python-dateutil`
    -   (Optional) `anthropic` or `openai` for live generation.

2.  **Configuration:**
    -   Create `publisher_config.json` with keys for each account:
    ```json
    {
        "ddas-devblog": {
            "posting_key": "YOUR_POSTING_KEY",
            "private_key": "YOUR_ACTIVE_KEY"
        }
    }
    ```

## Usage

**Dry Run (Default):**
Simulates generation and publishing without broadcasting to Hive.
```bash
python3 orchestrator.py
```

**Live Publishing:**
```bash
python3 orchestrator.py --publish --no-dry-run --config publisher_config.json
```

**Testing:**
Run the unit tests:
```bash
python3 -m unittest content/automation/tests/test_hive_publish.py
```

## MVP Features
-   Daily content generation for 5 accounts.
-   Content queuing and scheduling.
-   Markdown formatting and image prompt generation.
-   Dry-run mode for verification.
