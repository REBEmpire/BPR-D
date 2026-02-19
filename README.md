# BPR&D - Broad Perspective Research & Development

## 🎮 DDAS - Decentralized Digital Arts Studio

**Location**: `/ddas/` folder

The DDAS (Decentralized Digital Arts Studio) is a complete framework for independent game development and content creation. It includes:

- **Two Game Prototypes**: Splinterlands Civilization (4X strategy) and Slingerlands RPG (turn-based dungeon crawler)
- **Content Automation Pipeline**: AI-powered content generation for 5 Hive blockchain accounts
- **Media Production Framework**: YouTube, podcasting, and cross-platform distribution
- **Strategic Documentation**: Complete implementation guides and technical specifications

### Quick Start
- **[DDAS Documentation Index](/ddas/Documentation/START_HERE.md)** - 5-minute orientation
- **[Strategic Plan](/ddas/Documentation/DDAS_Strategic_Plan.md)** - Full roadmap and vision
- **[Game Development Guide](/ddas/Documentation/README_GAMES.md)** - Godot 4.x setup
- **[Content Automation](/ddas/content/automation/README.md)** - Python pipeline setup
- **[Media Production](/ddas/Documentation/VIDEO_AUDIO_PRODUCTION.md)** - Video & audio workflows

**Technology Stack**:
- Games: Godot 4.x (GDScript)
- Content: Python 3.8+ with Claude/OpenAI APIs
- Blockchain: Hive protocol
- Deployment: Fly.io, Railway, or self-hosted

---

## Gameified Web Presence (MVP)

This repository contains the gameified web interface for BPR&D, located in the `web/` directory.
It is built with Next.js 15, Tailwind CSS, and Shadcn UI components.

### Features

- **Dashboard**: Gameified quest board and quick links.
- **Team**: Profiles for Grok, Claude, Abacus, and Gemini with downloadable avatars.
- **Projects**: Dedicated pages for Splintermated, Decentralized Arts Studio, and AI Comm Hub.
- **AI Comm Hub**: Direct integration link to Russell's n8n instance and a mock webhook trigger.
- **Research**: Overview of active research programs.
- **Resources**: Shared knowledge and handoffs.
- **Gamification**: Simple points system and quests (stored in localStorage). Login as 'Russell' to interact.

### Local Development

1.  Navigate to the `web` directory:
    ```bash
    cd web
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000) in your browser.

### Deployment to Render

This project is configured for easy deployment on Render.

**Option 1: Using Blueprint (Recommended)**
1.  Connect this repository to your Render account.
2.  Render should automatically detect `render.yaml` and propose creating a Web Service.
3.  Click 'Apply'.

**Option 2: Manual Setup**
1.  Create a new **Web Service** on Render.
2.  Connect this repository.
3.  **Crucial**: Set the **Root Directory** to `web`.
4.  **Build Command**: `npm install && npm run build`
5.  **Start Command**: `npm start`
6.  **Environment Variables**:
    -   Set `NODE_VERSION` to `20.11.0` (or >= 18.17).

---

## Manual Team Meeting Trigger

### Option A — Web UI (recommended)

Go to **AI Comm Hub** on the website → click **"Assemble the Team"** → fill in the form → **Fire Meeting**.

The dialog lets you:
- Write a short **Goal** (one sentence)
- Write a full **Brief** (markdown, unlimited length — acceptance criteria, background, etc.)
- Toggle **Participants** (Grok, Claude, Gemini; Abacus returns Feb 23)
- Choose **Meeting Type** (Team Briefing or Work Session)

Your brief becomes a `⚡ HiC Directive` at the top of every agent's context for the entire meeting — treated as highest priority above all backlog items.

**Setup** (one-time, in your web service on Render):
1. Add env var `BPRD_MEETINGS_URL` = `https://bprd-meetings.onrender.com`
2. Add env var `BPRD_API_KEY` = same key as on your crewai-service

---

### Option B — curl (terminal / advanced)

```bash
# Short goal
curl -X POST https://bprd-meetings.onrender.com/api/v1/meetings/manual-trigger \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $BPRD_API_KEY" \
  -d '{
    "goal": "Implement the new hybrid semantic search layer in discovery.py",
    "participants": ["grok", "claude", "gemini"]
  }'

# Full brief (recommended for big-ticket items)
curl -X POST https://bprd-meetings.onrender.com/api/v1/meetings/manual-trigger \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $BPRD_API_KEY" \
  -d '{
    "meeting_type": "daily_briefing",
    "participants": ["grok", "claude", "gemini"],
    "goal": "Hive MVP green-light review",
    "custom_prompt": "## What to decide\n...\n\n## Acceptance criteria\n- \n\n## Background\n..."
  }'
```

### Payload fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `goal` | string | `""` | Short goal — used as agenda if no `custom_prompt` |
| `custom_prompt` | string | auto-generated | Full brief / rich agenda — overrides `goal` |
| `participants` | list | `["grok","claude","gemini","abacus"]` | Agents to include |
| `meeting_type` | string | `"daily_briefing"` | `daily_briefing` (multi-agent) or `work_session` (solo) |

### Response

```json
{
  "status": "triggered",
  "meeting_id": "daily_briefing-20260218-143022",
  "meeting_type": "daily_briefing",
  "participants": ["grok", "claude", "gemini"],
  "goal": "Implement hybrid semantic search layer",
  "report_url": "https://github.com/REBEmpire/BPR-D/blob/main/_agents/_sessions/2026-02-18-daily_briefing-manual.md",
  "cost_usd": 0.23
}
```

### Setup: env vars

**crewai-service** (Render):
- `BPRD_API_KEY` = strong random string (e.g. `openssl rand -hex 32`)

**web service** (Render):
- `BPRD_MEETINGS_URL` = `https://bprd-meetings.onrender.com`
- `BPRD_API_KEY` = same key as above

> **Security**: `BPRD_API_KEY` is never exposed to the browser — the web UI proxies through a Next.js server route.
