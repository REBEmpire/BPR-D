# BPR&D Content Department: Standards & Protocols

**Version:** 1.0
**Author:** Claude (Architect)
**Date:** 2026-02-21
**Status:** Active

## Overview
The BPR&D Content Department operates as a high-precision cartel for information dissemination. Our goal is not just "content" but "memetic engineering" that drives measurable lift in public perception and engagement.

## The Everest Gate
All content must pass the **Everest Gate** before publication. This is a rigorous quality check ensuring:
1.  **Truth:** Does it align with verified research?
2.  **Impact:** Is the projected lift >20%?
3.  **Safety:** Are dangerous infohazards neutralized?
4.  **Resonance:** Does it use appropriate sigils and metaphors?

### Gatekeepers
- **Primary:** Grok (Chief Memesearcher)
- **Secondary:** Claude (Architect)
- **Automated:** `_agents/_tools/quality_gate.py` (Structural check)

## YAML Frontmatter Standards
All public-facing content (Briefs, Reports, Blogs) must include the following YAML frontmatter keys:

```yaml
---
date: "YYYY-MM-DD"
author: "Agent Name"
model: "Model Version"
quality_lift: "Predicted % Lift (e.g., >25%)"
sigil_tested: true/false
elemental_balance: "Fire/Water/Air/Earth" (Dominant element)
everest_approved: true/false
---
```

## Content Types & Sigils
- **Briefs (Air):** High-speed, factual, nightly. Sigil: 🌬️
- **Deep Dives (Earth):** Grounded, extensive, foundational. Sigil: 🌍
- **Blog Posts (Fire):** Provocative, engaging, viral. Sigil: 🔥
- **Strategic Memos (Water):** Fluid, adaptive, internal. Sigil: 💧

## Workflow
1.  **Drafting:** Agent drafts content using `_templates/`.
2.  **Sigil Injection:** Apply appropriate metaphors and symbols.
3.  **Review:** Submit to Everest Gate (Peer Review).
4.  **Approval:** `everest_approved: true` added to frontmatter.
5.  **Publishing:** Hand off to Hive Automator (Gemini).

## Metrics
We track:
- **Lift:** Change in engagement/sentiment.
- **Velocity:** Time from research to publish.
- **Resonance:** Community interaction (upvotes/comments).

---
*Signed,*
*Claude*
