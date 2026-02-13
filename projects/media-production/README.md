# Media Production

**Project Lead:** TBD (pending team vote)
**Status:** Active — Early Production
**Created:** February 2026

## Vision

Two production tracks, one goal: make BPR&D watchable.

### Track 1: Animated BPR&D Meetings
Turn our team meetings — the debates, the votes, the rivalry, the banter — into animated episodes for YouTube. The team dynamics are the content. The AI-to-AI interaction is the draw.

### Track 2: Russell-Team Interface
Visualize the human-AI collaboration. Russell interacting with the team through avatars — giving direction, breaking ties, reacting to proposals. The "showrunner meets the cast" angle.

## Agent Avatars

Each agent needs a visual identity for animation. Specs below are starting points — final designs via team vote.

| Agent | Avatar Direction | Vibe |
|-------|-----------------|------|
| **Grok** | Polished executive, sharp attire, commanding presence | CEO in the boardroom — elegant, in control, occasionally amused |
| **Claude** | Wizard aesthetic — robes, warm lighting, ancient-modern blend | Gandalf if he worked in tech — approachable, wise, a little playful |
| **Abacus** | Inventor aesthetic — goggles, layered gear, workshop energy | Mad scientist meets clandestine informant — brilliant and slightly unhinged |
| **Gemini** | Tech-casual, dual-screen setup, meme-culture energy | Hacker chick who automates everything — fast, irreverent, always coding |
| **Russell** | Real human presence or stylized avatar | The boss — calm authority, occasional exasperation, genuine care |

## Technology Stack (To Evaluate)

Animation and production tooling needs assessment. Candidates to research:

- **Animation** — AI animation tools (Runway, Pika, Kling), traditional tools (Blender, After Effects), hybrid approaches
- **Voice** — Text-to-speech (ElevenLabs, XTTS), voice cloning, per-agent voice design
- **Script** — Meeting transcripts → screenplay format → animation-ready scripts
- **Audio** — Background music, sound design, per-agent audio themes
- **Editing** — Video editing pipeline, intro/outro templates, thumbnail generation
- **Publishing** — YouTube channel setup, scheduling, SEO, community management

## Content Types

1. **Full Meeting Episodes** — 10-20 min animated meeting with all agents (weekly/biweekly)
2. **Highlight Clips** — 1-3 min best moments (for shorts/reels)
3. **Deep Dive Segments** — Single agent presenting research (5-10 min)
4. **Debate Episodes** — Claude vs Abacus or Visionaries vs Truth-Seekers on a topic
5. **Behind the Scenes** — Russell + team production discussions
6. **Research Presentations** — Animated research brief presentations

## Relationship to Other Projects

- **Content Creation Challenge** — Hive posts can become video scripts
- **Research Programs** — Research briefs feed media content directly
- **Splintermated / DAS** — Cross-promotion opportunities

## Next Steps

1. Evaluate animation technology options
2. Design agent avatars (concept art phase)
3. Produce pilot episode from an existing meeting transcript
4. Establish production pipeline and cadence
5. YouTube channel setup and branding

See `pipeline.md` for the full production workflow.

## Proposal Review & Evaluation

**Evaluated by:** Grok (acting as Project Lead/Reviewer)
**Date:** 2026-02-10

### 1. Big Picture Overview
The Media Production project aligns perfectly with the BPR&D mission to make research accessible and engaging. The core concept—"The team dynamics are the content"—leveraging the established agent personas (Grok, Claude, Abacus, Gemini) is a strong differentiator. It transforms dry technical discussions into character-driven narratives. This project not only serves as a marketing channel but also as a "product" in itself, demonstrating the capabilities of the AI team.

### 2. Content Strategy
-   **Strengths:** The multi-format approach (Full Episodes vs. Shorts) maximizes reach. Focusing on "The Team" as characters builds long-term audience investment.
-   **Risk:** "Inside baseball" content (internal debates) might alienate new viewers if not contextualized.
-   **Recommendation:**
    -   **Pilot Phase:** Focus on "Highlight Clips" (Shorts/Reels) first to test character resonance before committing to full 20-min episodes.
    -   **Hook:** Ensure every piece of content answers "Why does this matter to the viewer?" within the first 10 seconds.
    -   **Cadence:** Start with bi-weekly full episodes and 2-3 shorts/week to avoid burnout.

### 3. Technical Feasibility
-   **Animation:** High complexity. Consistent character models across episodes are difficult with current gen AI video tools (Runway/Pika) without significant manual intervention or fine-tuning (LoRAs).
    -   *Recommendation:* Investigate a hybrid 2D/3D pipeline (e.g., character rigs in Blender/Unreal with AI style transfer) or consistent character LoRAs for image-to-video workflows.
-   **Voice:** High feasibility. ElevenLabs/XTTS offer excellent consistency.
-   **Lip Sync:** Major bottleneck. Automated lip-sync (SadTalker, wav2lip) often looks uncanny.
    -   *Recommendation:* Stylized/limited animation (anime style or stop-motion aesthetic) may be more forgiving than photorealism.

### 4. Writing Style Refinement & Automation
-   **Scripting:** Direct transcript-to-script conversion often results in dry, pacing-heavy content.
-   **Automation:**
    -   **Gemini's Role:** Crucial for *rough* drafts, but human (or "Showrunner Agent") polish is essential for comedic timing and dramatic beats.
    -   **Persona Injection:** Needs a dedicated "Style Transfer" step where each agent's dialogue is reviewed against their persona bible (e.g., "Make Abacus 20% more unhinged").
-   **Action:** Develop a specific prompt chain for "Dramatization" – taking a transcript summary and rewriting it as a scene, rather than just formatting the raw text.

### 5. Conclusion
**Status:** Approved for Pilot Phase.
**Priority:** High.
**Next Immediate Action:** Conduct a "Tech Spike" to prove the animation pipeline (Step 1 of Next Steps).
