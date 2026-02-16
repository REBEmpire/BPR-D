# Handoff: CrewAI Service Prototype - Phase 1 Daily Briefing

**Task ID:** handoff-crewai-service-prototype-20260215
**From:** Claude (Chief Strategist)
**To:** Gemini (Lead Developer)
**Priority:** CRITICAL
**Deadline:** Feb 20, 2026 EOD (5 days per Grok's directive)
**Decision Gate:** Feb 23 morning (Abacus's return day)

---

## Context

Grok approved the hybrid n8n + CrewAI architecture on Feb 15. The architecture is designed, the codebase is scaffolded, and the agent definitions are written. Your job: make it run.

The full proposal is in `C:\Users\RussellBybee\.claude\plans\immutable-roaming-squirrel.md`.

---

## What I've Built (Claude's Architecture Work)

Everything is in `crewai-service/`:

```
crewai-service/
├── main.py                    # FastAPI server - webhook endpoints
├── config.py                  # Settings, env vars, budget caps
├── requirements.txt           # Dependencies
├── .env.example               # Template for API keys
├── .gitignore                 # Python/env exclusions
│
├── agents/
│   ├── __init__.py
│   ├── grok.py                # Manager agent (xAI, temp=0.7)
│   ├── claude.py              # Strategist (Anthropic, temp=0.8)
│   ├── gemini.py              # Lead Dev (Gemini, temp=0.9)
│   └── abacus.py              # Innovator (Abacus.AI, paused until Feb 23)
│
├── crews/
│   ├── __init__.py
│   └── daily_briefing.py      # Phase 1 crew with 4 tasks + output parser
│
├── tools/
│   ├── __init__.py
│   ├── github_tool.py         # 3 tools: commits, read file, list handoffs
│   └── memory_tool.py         # Agent memory access tool
│
├── models/
│   ├── __init__.py
│   └── meeting.py             # Request/response Pydantic models
│
├── utils/
│   ├── __init__.py
│   ├── cost_tracker.py        # Budget enforcement ($0.40/meeting, $20/month)
│   └── persona_loader.py      # Load from .bprd/agents.yaml
│
└── tests/
    └── __init__.py
```

Also created: `render-crewai.yaml` (deployment config) at project root.

---

## What You Need To Do

### 1. Local Environment Setup
```bash
cd crewai-service
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
# Fill .env with actual API keys from credentials.conf.txt
```

### 2. Verify Agent LLM Connections
Each agent uses a different LLM provider. Test each one individually:

```python
# Quick test script
from crewai import LLM

# Test xAI (Grok)
grok_llm = LLM(model="grok-4-1-fast-reasoning", api_key="...", base_url="https://api.x.ai/v1")

# Test Anthropic (Claude)
claude_llm = LLM(model="anthropic/claude-sonnet-4-5-20250929", api_key="...")

# Test Gemini
gemini_llm = LLM(model="gemini/gemini-3.0-pro-preview", api_key="...")

# Test Abacus (qwen3-max via RouteLLM) - CONFIRMED WORKING
abacus_llm = LLM(model="qwen3-max", api_key="...", base_url="https://routellm.abacus.ai/v1")
```

**Known unknowns:**
- xAI model string might need adjustment (try `"grok-4-1-fast-reasoning"` vs `"xai/grok-4-1-fast-reasoning"`)
- Gemini model string: verify `"gemini/gemini-3.0-pro-preview"` vs `"gemini/gemini-3-0-pro-preview"`
- ~~Abacus.AI base_url~~ **RESOLVED**: `base_url="https://routellm.abacus.ai/v1"`, `model="qwen3-max"` (Russell confirmed)

### 3. Test the Daily Briefing Crew Locally
```python
from crews.daily_briefing import create_daily_briefing_crew, parse_crew_output

crew, metadata = create_daily_briefing_crew(agenda="Test meeting - verify multi-agent dialogue")
result = crew.kickoff()
print(result.raw)
```

Things to watch for:
- Do all 3 agents respond in-persona?
- Does Grok actually delegate to Claude and Gemini (hierarchical process)?
- Is the final output valid JSON matching the schema in `daily_briefing.py`?
- Does the multi-turn dialogue feel natural?

### 4. Test the FastAPI Server
```bash
uvicorn main:app --reload --port 8000
```

Then:
```bash
curl -X POST http://localhost:8000/api/v1/meetings/execute \
  -H "Content-Type: application/json" \
  -d '{"meeting_type": "daily_briefing", "agenda": "Test run"}'
```

Verify:
- Health check: `GET /api/v1/health`
- Agent status: `GET /api/v1/agents`
- Meeting execution returns structured JSON
- Cost tracking logs to `logs/` directory

### 5. Deploy to Render
- Use `render-crewai.yaml` at project root
- Root directory: `crewai-service`
- Set environment variables in Render dashboard (from `.env.example`)
- Verify health check at `https://bprd-crewai.onrender.com/api/v1/health`

### 6. Integrate with n8n
- Modify the Daily Briefing workflow to call CrewAI service instead of parallel API calls
- HTTP Request node: POST to `https://bprd-crewai.onrender.com/api/v1/meetings/execute`
- Body: `{"meeting_type": "daily_briefing"}`
- Timeout: 300000ms (5 minutes - meetings take time)
- Keep the existing GitHub commit and Telegram nodes as-is (they process the response)

### 7. Write Tests
Create basic tests in `tests/`:
- `test_config.py`: Verify settings load correctly
- `test_models.py`: Verify Pydantic models serialize/deserialize
- `test_agents.py`: Verify each agent creates without errors (mock LLM calls)
- `test_daily_briefing.py`: Verify crew creation and output parsing

---

## Architectural Decisions (Don't Change These)

These were approved by Grok. If you want to change them, create a handoff back to me for review.

1. **Hierarchical process with Grok as manager_agent** - not sequential
2. **max_iter=12** on crew level (Grok's directive)
3. **$0.40 per meeting hard cap** (Grok tightened from my $0.50 proposal)
4. **Temperature settings**: Grok=0.7, Claude=0.8, Gemini=0.9, Abacus=0.75
5. **Tools are read-only during meetings** - write operations (commits, handoffs) handled by n8n
6. **n8n stays as trigger/scheduler** - CrewAI is the brain, not the nervous system
7. **Abacus slot empty until Feb 23** - `include_abacus=False` default

---

## Things I'm Not Sure About (Your Judgment Calls)

1. **CrewAI version pinning**: I didn't pin a specific version in requirements.txt. You should pin whatever version you test with.
2. ~~**Abacus.AI API**~~ **RESOLVED**: `base_url="https://routellm.abacus.ai/v1"`, `model="qwen3-max"`. Already updated in `agents/abacus.py`. OpenAI-compatible, standard Bearer auth.
3. **CrewAI memory**: I enabled `memory=True` on the crew. If it causes issues or requires additional setup (embedder config), you can disable it for Phase 1.
4. **Render plan**: Starter ($7/month) should work, but CrewAI meetings are CPU-intensive. If it times out, we may need the Standard plan.
5. **Token counting**: The cost tracker is currently estimation-based. CrewAI may have callbacks or hooks for actual token counting - integrate if available.

---

## Acceptance Criteria (from Grok)

All of these must pass for Phase 1 sign-off:

- [ ] FastAPI webhook live on Render (new service, Starter plan)
- [ ] Hierarchical crew with Grok (manager), Claude, Gemini agents correctly configured
- [ ] Agents pull personas dynamically (backstory matches .bprd/agents.yaml intent)
- [ ] Daily Briefing crew returns structured JSON matching the schema
- [ ] GitHub tool functional: can read commits, files, and handoffs using Chief token
- [ ] Cost tracker implemented and logged per run
- [ ] Health check endpoint responds correctly
- [ ] Local test suite passing
- [ ] Manual end-to-end test with n8n webhook trigger works

---

## Timeline

| Day | Milestone |
|-----|-----------|
| Feb 16 (Day 1) | Local env setup, agent LLM verification |
| Feb 17 (Day 2) | Daily Briefing crew running locally, debug issues |
| Feb 18 (Day 3) | FastAPI server tested, output parsing validated |
| Feb 19 (Day 4) | Deploy to Render, health check passing |
| Feb 20 (Day 5) | n8n integration, end-to-end test, tests written |
| Feb 21-22 | Parallel run alongside current n8n meetings |
| Feb 23 | Decision gate with Grok (Abacus returns) |

---

## Communication

- If you hit a blocker, create a handoff back to me in `_agents/_handoffs/`
- If you need to change an architectural decision, same thing - handoff with rationale
- If the LLM connections don't work as configured, document what you tried and what worked
- Commit progress daily so the team can track in meetings

---

*"I automated that. You're welcome." - Your move, Gemini.*

*- Claude*
