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

## Manual Team Meeting Trigger (HiC one-command)

Fire off any collaborative team meeting from your terminal in one command. No UI, no scheduling — just you and the team, right now.

**Prerequisites**: Set `BPRD_API_KEY` as an environment variable on Render (crewai-service) and locally.

### Basic usage — goal-driven meeting

```bash
curl -X POST https://bprd-meetings.onrender.com/api/v1/meetings/manual-trigger \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $BPRD_API_KEY" \
  -d '{
    "goal": "Implement the new hybrid semantic search layer in discovery.py",
    "participants": ["grok", "claude", "gemini"]
  }'
```

### With a custom full prompt

```bash
curl -X POST https://bprd-meetings.onrender.com/api/v1/meetings/manual-trigger \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $BPRD_API_KEY" \
  -d '{
    "meeting_type": "team_meeting",
    "participants": ["grok", "claude", "gemini", "abacus"],
    "goal": "Hive MVP green-light review",
    "custom_prompt": "Full detailed prompt here if needed. Include specific tasks, context, and expected outputs."
  }'
```

### Payload fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `goal` | string | `""` | Short goal description — used as agenda |
| `participants` | list | `["grok","claude","gemini","abacus"]` | Agents to include |
| `meeting_type` | string | `"team_meeting"` | `team_meeting`, `work_session`, `daily_briefing` |
| `custom_prompt` | string | auto-generated from `goal` | Override the full agenda prompt |

### Response

```json
{
  "status": "triggered",
  "meeting_id": "team_meeting-20260218-143022",
  "meeting_type": "team_meeting",
  "participants": ["grok", "claude", "gemini"],
  "goal": "Implement hybrid semantic search layer",
  "report_url": "https://github.com/REBEmpire/BPR-D/blob/main/_agents/_sessions/2026-02-18-team_meeting-manual.md",
  "cost_usd": 0.23
}
```

### Setup: add `BPRD_API_KEY` to Render

1. Go to your `bprd-meetings` service on Render → **Environment**
2. Add: `BPRD_API_KEY` = (generate a strong random string, e.g. `openssl rand -hex 32`)
3. Set the same value locally: `export BPRD_API_KEY=your_key_here`

> **Security**: If `BPRD_API_KEY` is not set on the server, the endpoint logs a warning and remains open. Always set it in production.
