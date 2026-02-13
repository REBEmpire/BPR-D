# DDAS Content Automation - Setup Guide

Complete guide for setting up and running the daily content generation and publishing pipeline.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your environment
cp publisher_config.json.example publisher_config.json
# Edit publisher_config.json with your Hive account keys

# 3. Test content generation (dry run, no publishing)
python orchestrator.py --provider claude

# 4. Generate and publish (requires valid config)
python orchestrator.py --provider claude --publish --no-dry-run
```

## System Overview

The DDAS content pipeline consists of:

1. **Content Generator** (`content_generator.py`)
   - Generates articles, stories, guides, news using AI
   - Supports multiple AI backends (Claude, OpenAI, Ollama)
   - Batch processing for multiple accounts

2. **Hive Publisher** (`hive_publisher.py`)
   - Publishes content to Hive blockchain
   - Manages content queue
   - Handles scheduling and retries

3. **Orchestrator** (`orchestrator.py`)
   - Coordinates the daily workflow
   - Manages 5 Hive accounts
   - Generates reports and metrics

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (for API calls)
- Hive account(s) with posting key

### Step 1: Clone/Setup

```bash
cd content/automation
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements file** (`requirements.txt`):
```
requests>=2.28.0
python-dateutil>=2.8.2
beespy>=0.2.0              # For Hive blockchain interaction
pydantic>=1.9.0            # For data validation
python-dotenv>=0.20.0      # For environment variables
```

### Step 4: Configure API Keys

Create `publisher_config.json`:

```json
{
  "ddas-devblog": {
    "posting_key": "YOUR_POSTING_PRIVATE_KEY_HERE",
    "private_key": "YOUR_ACTIVE_KEY_HERE"
  },
  "ddas-lore": {
    "posting_key": "YOUR_POSTING_PRIVATE_KEY_HERE",
    "private_key": "YOUR_ACTIVE_KEY_HERE"
  },
  "ddas-strategy": {
    "posting_key": "YOUR_POSTING_PRIVATE_KEY_HERE",
    "private_key": "YOUR_ACTIVE_KEY_HERE"
  },
  "ddas-community": {
    "posting_key": "YOUR_POSTING_PRIVATE_KEY_HERE",
    "private_key": "YOUR_ACTIVE_KEY_HERE"
  },
  "ddas-news": {
    "posting_key": "YOUR_POSTING_PRIVATE_KEY_HERE",
    "private_key": "YOUR_ACTIVE_KEY_HERE"
  },
  "ai_provider": {
    "type": "claude",
    "api_key": "YOUR_CLAUDE_API_KEY"
  }
}
```

**IMPORTANT**: Never commit `publisher_config.json` to git. Add to `.gitignore`:
```
publisher_config.json
.env
*.key
credentials.*
```

### Step 5: Environment Variables (Alternative to Config File)

Create `.env` file:
```
HIVE_ACCOUNT_DEVBLOG=ddas-devblog
HIVE_POSTING_KEY_DEVBLOG=your_key_here

CLAUDE_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here (if using OpenAI)
```

Then load in scripts:
```python
from dotenv import load_dotenv
import os

load_dotenv()
posting_key = os.getenv("HIVE_POSTING_KEY_DEVBLOG")
```

## Configuration

### Publisher Configuration

Each Hive account needs:
- **Account name**: The Hive username
- **Posting key**: Private key for posting content (NOT the active/owner key)
- **Private key** (optional): Active key for token transfers

**Finding Your Keys**:
1. Go to https://hive.blog/@your-account
2. Click settings icon
3. Under "Keys" - you'll see posting key
4. **KEEP THESE PRIVATE** - treat like passwords

### AI Provider Configuration

Supported providers:

#### Claude (Recommended)
```bash
export CLAUDE_API_KEY="sk-ant-..."
python orchestrator.py --provider claude
```

#### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
python orchestrator.py --provider openai
```

#### Ollama (Local, Free)
Requires Ollama running locally:
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
ollama serve  # Run in background
python orchestrator.py --provider ollama
```

## Usage

### Basic Content Generation (No Publishing)

```bash
# Generate content for all accounts (dry run)
python orchestrator.py --provider claude
```

Output:
- Console logs with generation progress
- Generated content saved to `generated_content/` directory
- Session report in `session_reports/`

### Publish to Hive

```bash
# Generate and publish to Hive (with dry-run first)
python orchestrator.py --provider claude --publish

# Actually broadcast to blockchain (careful!)
python orchestrator.py --provider claude --publish --no-dry-run
```

### Generate Single Account

```python
# In your own script
from content_generator import ContentGenerator, ContentPrompt

gen = ContentGenerator()
prompt = ContentPrompt(
    account="ddas-devblog",
    content_type="devlog",
    title="Weekly Update",
    topic="This week's progress",
    tags=["development", "update"],
    tone="technical",
    length="medium"
)
result = gen.generate_content(prompt)
```

### Batch Generation

```python
from content_generator import PromptLibrary, ContentGenerator

gen = ContentGenerator()
prompts = PromptLibrary.get_dev_blog_prompts() + \
          PromptLibrary.get_lore_prompts() + \
          PromptLibrary.get_strategy_prompts()

results = gen.generate_batch(prompts)
```

### Schedule Posts

```python
from hive_publisher import HivePublisher
from datetime import datetime, timedelta

publisher = HivePublisher("ddas-devblog", "your_posting_key")

# Schedule for tomorrow at 9 AM
tomorrow_9am = datetime.now().replace(hour=9) + timedelta(days=1)

publisher.schedule_post(
    title="Tomorrow's Post",
    content="This will be published tomorrow",
    tags=["update"],
    publish_time=tomorrow_9am
)
```

## Automation Scheduling

### Linux/Mac - Crontab

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM UTC
0 9 * * * cd /path/to/DDAS/content/automation && python orchestrator.py --provider claude --publish --no-dry-run >> ddas.log 2>&1
```

### Windows - Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "DDAS Daily Content"
4. Trigger: Daily at 9:00 AM
5. Action: Start program
   - Program: `C:\Python39\python.exe`
   - Arguments: `C:\path\to\orchestrator.py --provider claude --publish --no-dry-run`
6. Advanced: Check "Run with highest privileges"

### GitHub Actions - Free Cloud Scheduler

Create `.github/workflows/ddas-daily.yml`:

```yaml
name: DDAS Daily Content

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
  workflow_dispatch:     # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r content/automation/requirements.txt

      - name: Generate and publish content
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          HIVE_PUBLISHING_CONFIG: ${{ secrets.HIVE_CONFIG }}
        run: |
          cd content/automation
          python orchestrator.py --provider claude --publish --no-dry-run
```

Then add secrets in GitHub:
1. Go to Settings → Secrets
2. Add `CLAUDE_API_KEY`
3. Add `HIVE_CONFIG` (base64 encoded)

## Content Templates

Each account type has a template:

- `content/templates/devblog_template.md` - Development updates
- `content/templates/lore_template.md` - Stories and lore
- `content/templates/strategy_template.md` - Game guides
- `content/templates/community_template.md` - Community spotlights
- `content/templates/news_template.md` - Announcements

### Using Templates

```python
from content_generator import ContentPrompt

# Template is applied automatically based on content_type
prompt = ContentPrompt(
    account="ddas-devblog",
    content_type="devlog",  # Applies devblog_template
    title="Weekly Update",
    # ... rest of prompt
)
```

## Output Structure

### Generated Content

Files saved to `generated_content/` folder:

```json
{
  "success": true,
  "prompt": {
    "account": "ddas-devblog",
    "content_type": "devlog",
    "title": "...",
    "topic": "...",
    "tags": [...]
  },
  "generated_at": "2026-02-12T09:30:00",
  "content": "# Full article markdown here",
  "image_prompt": "AI image prompt",
  "tags": ["development", "update"]
}
```

### Session Reports

Files saved to `session_reports/`:

```json
{
  "session": {
    "start_time": "2026-02-12T09:00:00",
    "content_generated": 5,
    "content_published": 5,
    "errors": 0
  },
  "generation": {
    "accounts": {
      "ddas-devblog": {
        "generated": [...],
        "errors": []
      }
    }
  },
  "publishing": {
    "published": [...],
    "errors": [...]
  }
}
```

## Monitoring & Logging

### Log Files

- `ddas_orchestrator.log` - Main execution log
- Console output - Real-time progress

### Checking Recent Runs

```bash
# View last 20 log entries
tail -20 ddas_orchestrator.log

# Watch log in real-time
tail -f ddas_orchestrator.log
```

### Error Handling

If a post fails to publish:

1. Check the error message in logs
2. Verify Hive account is funded (needs ~0.01 HIVE for gas)
3. Verify posting key is correct
4. Check API rate limits (beespy has limits)
5. Retry with: `python orchestrator.py --provider claude --publish --no-dry-run`

## Content Quality Tips

### For Better AI-Generated Content

1. **Be Specific in Prompts**: Detailed prompts produce better content
2. **Iterate**: If first draft isn't great, regenerate
3. **Review**: Always review AI content before publishing
4. **Add Personal Touch**: Edit to match your voice
5. **Use Templates**: Templates ensure consistent structure

### Prompt Engineering

```python
# Good prompt (specific)
ContentPrompt(
    title="Building a Civilization: Resource Management",
    topic="How to balance resources in early game",
    additional_instructions="Include 2-3 specific strategies with examples. Write for intermediate players."
)

# Generic prompt (less effective)
ContentPrompt(
    title="Game Guide",
    topic="How to play"
)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'beespy'"
```bash
pip install beespy
```

### "Invalid posting key"
- Verify key format (should be long hexadecimal string)
- Ensure you copied the posting key, not active key
- Try re-generating keys in Hive

### "API rate limit exceeded"
- Reduce batch size
- Add delays between requests
- Use local Ollama instead of cloud APIs

### "No content generated"
- Check AI provider is configured
- Verify API keys are set
- Check internet connection
- Review orchestrator logs

## Performance Optimization

### For Large Batch Operations

```python
# Limit concurrent API calls
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(gen.generate_content, p) for p in prompts]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]
```

### Cache Generated Content

```python
# Check if content already exists before regenerating
import hashlib

def get_content_hash(prompt: ContentPrompt) -> str:
    return hashlib.md5(f"{prompt.account}_{prompt.title}".encode()).hexdigest()

# Skip if already generated today
if hash in today_generated:
    continue
```

## Advanced Usage

### Custom Prompt Library

```python
# Create your own prompts
from content_generator import ContentPrompt

my_prompts = [
    ContentPrompt(
        account="ddas-custom",
        content_type="article",
        title="Custom Topic 1",
        topic="Specific topic for your account",
        tags=["custom"],
        tone="technical",
        length="long"
    ),
    # ... more prompts
]

gen.generate_batch(my_prompts)
```

### Webhook Integration

```python
# Notify Discord on publish
import requests

def notify_discord(content_title: str, url: str):
    webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK"
    requests.post(webhook_url, json={
        "content": f"✅ Published: {content_title}\n{url}"
    })
```

## Support & Resources

- **Hive Dev Docs**: https://developers.hive.io/
- **Orchestrator Logs**: Check `ddas_orchestrator.log`
- **GitHub Issues**: Report bugs and feature requests

---

**Version**: 0.1.0-alpha
**Last Updated**: 2026-02-12
**Status**: Active Development

Questions? Open an issue or ask in Discord!
