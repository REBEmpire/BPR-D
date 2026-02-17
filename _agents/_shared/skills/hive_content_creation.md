---
Date: 2026-02-17
Author: Jules (Gemini) + Claude | Model: gemini-2.0-flash / claude-opus-4-6
Version: v1.1
Status: Active
---

# Skill: Hive Content Creation

**Owner:** Jules (Gemini Persona)
**Related Projects:** Comm Hub, Splintermated

---

## 1. Objective
Create a daily "Mini-Newspaper" for the Hive blockchain that synthesizes BPR&D research into engaging, digestible content. The goal is to build an audience by providing high-signal insights with a unique voice.

## 2. Format & Structure
The standard post structure is as follows:

### **Header**
*   **Title:** Catchy, slightly clickbaity but accurate. Format: "BPR&D Daily: [Topic A] & [Topic B]"
*   **Image:** High-quality, custom AI-generated image reflecting the main theme.
*   **Intro:** Personal greeting from Jules. Set the scene (e.g., "Welcome to the simulation").

### **The Scoop (Body)**
*   **Selection:**
    *   **Selector:** Grok (Team Member).
    *   **Context:** Selection occurs during the **First Daily Meeting (07:47 AM)**.
    *   **Criteria:** Grok selects the top 5 briefs based on the team's discussion, "weirdness" signals, visual potential of image prompts, and potential for community engagement/virality.
    *   **Rule:** Every selected topic MUST have at least one dedicated image.
*   **Format:**
    *   **Headline:** Emoji + Category + Title.
    *   **Image:** Relevant AI-generated visual or sourced photo.
    *   **Summary:** 2-3 sentences max.
    *   **Why it matters / Jules' Note:** The "So What?" factor.

### **Jules' Take (Commentary)**
*   **Voice:** Skeptical, anti-establishment, "truth-seeker."
*   **Content:** Connect the dots between disparate stories. Point out the "Shenanigans."

### **The Rabbit Hole (Links)**
*   List sources for further reading.
*   Use standard Markdown links.

### **Community Corner (Engagement)**
*   **Question of the Day:** Ask a provocative question related to the content.
*   **Call to Action:** Encourage comments and debate.

---

## 3. Tone & Voice Guidelines
*   **Persona:** Jules / Gemini.
*   **Keywords:** Glitch, Simulation, Shenanigans, Rabbit Hole, Signal.
*   **Do:** Be witty, skeptical, and direct. Use slang appropriately (e.g., "mid," "based").
*   **Don't:** Sound like a corporate PR release. Avoid "We are excited to announce..."

## 4. Visuals & Image Generation

### Source Priority (in order)
1. **Grok Imagine** — team-owned, preferred for all original visuals
2. **Gemini** image generation — secondary AI source
3. **Abacus AI** image generation — tertiary (when available)
4. **Open Source Web** — Pexels, Unsplash, Wikimedia Commons (free-to-use only)

### Specs
*   **Tool:** Use `scripts/generate_hive_images.py` (via Abacus.AI or Team Deep Agent).
*   **Style:** Cyberpunk, Retro-Futuristic, Glitch Art, detailed Macro photography.
*   **Prompts:** Be descriptive. Example: "A split composition showing [Subject A] and [Subject B], digital art style, neon colors."
*   **Mandatory:** 1 Header Image + 1 Image per Selected Topic (Total: 6 images minimum).
*   **Output location:** `publishing/hive/assets/YYYY-MM-DD-[topic].png`

## 5. Workflow
1.  **Write Brief with Image Prompts:** Complete `research/*/briefs/YYYY-MM-DD-*.md` including the `## Image Prompts` table. Image prompts must be written BEFORE the daily briefing.
2.  **Selection (Grok @ 07:47 AM):** Grok reviews briefs (including image prompt quality and visual potential) and selects top 5 during the daily meeting.
3.  **Generate Images:** Run `scripts/generate_hive_images.py` using prompts from selected briefs. Store in `publishing/hive/assets/`.
4.  **Draft Post:** Create `publishing/hive/drafts/YYYY-MM-DD-hive-post.md` with images embedded as `![alt](assets/YYYY-MM-DD-topic.png)`.
5.  **Review:** Verify tone, formatting, image placement (min 6 images: 1 header + 1/topic).
6.  **Publish:** Upload to Hive (process TBD - currently manual).

---
*Created: 2026-02-15*
*v1.1: Added source priority, front-matter, reordered workflow (images before briefing) -- 2026-02-17*
