---
Date: 2026-02-17
Author: Russell (Human) + Grok | Model: grok-4
Version: v1.1
Status: Active
---

# Cost Governance Framework

## Overview

The BPR&D team operates under two distinct cost management pathways, reflecting the difference between **automated agent work** (delegated to agents) and **manual human-led work** (requiring Russell's account and pre-approval).

---

## Pathway 1: Automated Agent Work (API-Driven)

**Scope:** Daily meetings, research generation, content automation, code tasks—work agents execute via their LLM APIs.

**Budget:**
- **Team monthly cap**: $20/month (API costs across all agents)
- **Per-meeting hard cap**: $0.75 (enforced by `crewai-service/utils/cost_tracker.py`)
- **Status tracking**: Actual token counts logged from each API call

**Cost limits per agent:**
- **Grok (xAI/Grok 4)**: $5/month (meeting leadership, synthesis)
- **Claude (Anthropic)**: $6/month (architecture, strategy)
- **Gemini (Google)**: $5/month (research briefs, code generation)
- **Abacus (Abacus.AI)**: $4/month (deep analysis, investigation)

**Request process (Low Friction):**
If an agent discovers they're approaching their monthly cap or needs extra budget for a big push:
1. Add request to their `Context/active.md` file
   - Section: "API Budget Request"
   - Include: What they need (e.g., "2x daily briefs = +$2/month"), why, timeline
2. Russell approves in 24-48 hours
3. Agent logs actual spend for accountability

**Approval criteria:**
- Is this work valuable to BPR&D?
- Is the request reasonable ($1-3 extra/month)?
- Can we absorb it in the $20/month team budget?

---

## Pathway 2: Manual Work (Russell-Led, Pre-Approval Required)

**Scope:** Complex human-supervised tasks, large batch processing, experimental work, or intensive research synthesis that requires Russell's account and extended interaction time.

**Cost structure:**
- Uses Russell's subscription account(s) and API rate limits
- Prevents agent cost overruns by centralizing intensive work
- Enables high-quality, unrestricted work (no per-call budget panic)

**Request process (High Friction, Intentional):**
Agents write `HiC_Needed.md` when they identify work that should be human-supervised:

1. **File location:** `_agents/[agent]/HiC_Needed_[YYYYMMDD]_[description].md`
2. **Content required:**
   - What I'm Doing: Clear description
   - What I Want to Accomplish: Goals and outcomes
   - Preferred Prompt(s): Specific, detailed prompts Russell should use (copy-paste ready)
   - Estimated Effort: Time and resources needed
   - Rationale: Why this needs manual work instead of automated

3. **Russell reviews** and decides:
   - **Approved**: Work is valuable, fits roadmap, execute as described
   - **Denied**: Too expensive, wrong priority, or can be automated
   - **Negotiated**: "I can do half of this today, defer the rest to next week"

4. **Execution:** Russell uses the preferred prompts and logs the work
5. **Result:** Agent receives output and integrates into their work stream

**Examples of HiC_Needed work:**
- "I need Russell to do a 2-hour multi-agent dialogue about media production strategy" (Gemini)
- "Synthesize all 9 research topics into a cohesive narrative for the launch" (Abacus)
- "Build a custom analysis tool for processing Hive blockchain data" (Claude)

---

## Cost Tracking & Transparency

**What we measure:**
- API calls per agent (daily)
- Token counts per API provider (Grok, Anthropic, Google, Abacus)
- Meeting costs (hard cap $0.75)
- Manual work requests and approvals

**Where it's tracked:**
- Automated: `crewai-service/utils/cost_tracker.py` (per-meeting)
- Visible: Each agent's `Context/active.md` (requested vs. approved)
- Approval log: `_agents/_hic_approvals.md` (Russell's decisions)

**Monthly review:**
Russell conducts cost review on Feb 23 (also Abacus usage reset), Mar 23, etc.
- Verify team stayed under $20/month
- Approve or deny pending API requests
- Adjust allocations for next month if needed

---

## Hard Rules

1. **No agent can exceed their monthly cap without explicit approval**
2. **No manual work (HiC_Needed) can proceed without Russell's written approval**
3. **Meeting service enforces $0.75/meeting hard stop** (kills job if exceeded)
4. **Cost tracking is transparent** (accessible to all agents via GitHub)
5. **Agents are accountable** for their budget usage; frivolous spending reflects poorly

---

## Philosophy

Cost governance isn't about being cheap—it's about being **intentional**. We have resources (Russell's accounts for unlimited manual work, $20/month for automation). The constraint forces us to:
- Prioritize high-value work
- Delegate to agents when it's cost-effective
- Escalate to Russell for complex work where his judgment matters
- Stay accountable for what we spend

This structure gives agents autonomy while respecting Russell's resources and maintaining trust.

---

## Related Documents
- `_agents/_hic_needed_template.md` — Template for manual work requests
- `crewai-service/utils/cost_tracker.py` — Meeting cost enforcement
- `_agents/_protocols.md` — Full team governance rules

