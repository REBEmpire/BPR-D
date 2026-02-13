# BPR&D - Broad Perspective Research & Development

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
