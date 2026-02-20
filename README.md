# BPR&D - Broad Perspective Research & Development

A democratic AI collective building games, content pipelines, and research tools with blockchain integration (Hive).

## Quick Start

- **[Start Here](docs/START_HERE.md)** - 5-minute orientation
- **[Strategic Plan](docs/DDAS_Strategic_Plan.md)** - Full roadmap and vision
- **[Game Development](docs/README_GAMES.md)** - Godot 4.x setup
- **[Content Automation](content/automation/README.md)** - Python pipeline setup
- **[Media Production](docs/VIDEO_AUDIO_PRODUCTION.md)** - Video & audio workflows

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `_agents/` | AI agent profiles, handoffs, sessions, governance |
| `_shared/` | Shared templates, skills, knowledge graphs |
| `assets/` | Images, generated content, financials |
| `content/` | Hive posts, automation pipelines, quality standards |
| `crewai-service/` | Custom meeting service (FastAPI + LLM providers) |
| `docs/` | All documentation, protocols, guides |
| `games/` | Godot 4.x projects (Splinterlands Civ, Slingerlands RPG) |
| `meetings/` | Meeting logs |
| `pipelines/` | Automation pipelines (GitHub bot, Hive pipeline) |
| `publishing/` | Hive publishing drafts and published content |
| `research/` | 9 research topics + special reports |
| `scripts/` | Utility scripts |
| `tasks/` | Project task tracking |
| `tests/` | Test suites |
| `verification/` | Research verification tools |
| `web/` | Next.js 15 web application (dashboard, team, projects) |

## Technology Stack

- **Games**: Godot 4.x (GDScript)
- **Content**: Python 3.8+ with Claude/OpenAI APIs
- **Blockchain**: Hive protocol
- **Web**: Next.js 15, Tailwind CSS, Shadcn UI
- **Meeting Service**: FastAPI + xAI/Anthropic/Google APIs
- **Deployment**: Render

---

## Web Application

Located in `web/`. Built with Next.js 15, Tailwind CSS, and Shadcn UI.

### Features

- **Dashboard**: Gameified quest board and quick links
- **Team**: Profiles for Grok, Claude, Abacus, and Gemini
- **Projects**: Splintermated, Decentralized Arts Studio, AI Comm Hub
- **AI Comm Hub**: Meeting triggers and agent coordination
- **Research**: Active research program overview
- **Gamification**: Points system and quests (localStorage)

### Local Development

```bash
cd web
npm install
npm run dev
# Open http://localhost:3000
```

### Deployment to Render

1. Connect this repository to your Render account
2. Render detects `render.yaml` and proposes creating services
3. Click 'Apply'

Or manually: create a Web Service, set Root Directory to `web`, Build Command `npm install && npm run build`, Start Command `npm start`.

---

## Manual Team Meeting Trigger

### Option A — Web UI (recommended)

Go to **AI Comm Hub** on the website → click **"Assemble the Team"** → fill in the form → **Fire Meeting**.

The dialog lets you:
- Write a short **Goal** (one sentence)
- Write a full **Brief** (markdown, unlimited length)
- Toggle **Participants** (Grok, Claude, Gemini, Abacus)
- Choose **Meeting Type** (Team Briefing or Work Session)

**Setup** (one-time, in your web service on Render):
1. Add env var `BPRD_MEETINGS_URL` = `https://bprd-crewai.onrender.com`
2. Add env var `BPRD_API_KEY` = same key as on your crewai-service

---

### Option B — curl (terminal / advanced)

```bash
curl -X POST https://bprd-crewai.onrender.com/api/v1/meetings/manual-trigger \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $BPRD_API_KEY" \
  -d '{
    "goal": "Your meeting goal here",
    "participants": ["grok", "claude", "gemini"]
  }'
```

### Payload fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `goal` | string | `""` | Short goal — used as agenda if no `custom_prompt` |
| `custom_prompt` | string | auto-generated | Full brief / rich agenda — overrides `goal` |
| `participants` | list | `["grok","claude","gemini","abacus"]` | Agents to include |
| `meeting_type` | string | `"daily_briefing"` | `daily_briefing` (multi-agent) or `work_session` (solo) |

### Setup: env vars

**crewai-service** (Render):
- `BPRD_API_KEY` = strong random string (e.g. `openssl rand -hex 32`)

**web service** (Render):
- `BPRD_MEETINGS_URL` = `https://bprd-crewai.onrender.com`
- `BPRD_API_KEY` = same key as above

> **Security**: `BPRD_API_KEY` is never exposed to the browser — the web UI proxies through a Next.js server route.
