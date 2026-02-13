# Task 003: Build AI Comm Hub

**To:** Jules | **Priority:** High | **Est:** 3-4 hrs

## Goal
Build the **AI Comm Hub** - Python orchestrator service that runs team meetings.

## This IS the AI Comm Hub
The orchestrator at `projects/ai-comm-hub/` IS the AI Comm Hub project. No separate repo.

## Structure
```
ai-comm-hub/
├── orchestrator.py      # Main entry
├── config.yaml          # Settings
├── requirements.txt     # httpx, pyyaml
├── agents/
│   ├── base.py          # BaseAgent ABC
│   ├── grok.py          # xAI (working)
│   └── claude.py        # Anthropic (working)
├── utils/
│   └── credentials.py   # Load from credentials.conf.txt
└── logs/
    └── (conversations saved here)
```

## Working API Examples

**Grok (xAI):**
```python
httpx.post("https://api.x.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": "grok-3-mini-beta", "messages": [...], "temperature": 0.8})
# Response: data["choices"][0]["message"]["content"]
```

**Claude (Anthropic):**
```python
httpx.post("https://api.anthropic.com/v1/messages",
    headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
    json={"model": "claude-sonnet-4-20250514", "max_tokens": 1000,
          "system": "...", "messages": [{"role": "user", "content": "..."}]})
# Response: data["content"][0]["text"]
```

## Credentials Loader
```python
# utils/credentials.py - parse credentials.conf.txt
def load_credentials(path="../../credentials.conf.txt"):
    creds = {}
    for line in open(path):
        if ":" in line and not line.startswith("#"):
            name, key = line.split(":", 1)
            creds[name.lower().strip().replace(" ", "_")] = key.strip()
    return creds
```

## MVP Features
1. Load agent profiles from `_agents/*/profile.md`
2. Call Grok to open meeting
3. Call Claude to respond
4. Print color-coded output to console
5. Save transcript to `logs/YYYY-MM-DD-meeting.md`

## Done When
```bash
python orchestrator.py
# Outputs colored meeting between Grok and Claude
# Saves transcript to logs/
```
