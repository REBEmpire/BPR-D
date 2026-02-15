# BPR&D Team Meetings - n8n Automation

**Workflow URL:** https://n8n.bprd.io/workflow/pDh6gPBEULb5kSx9

---

## Overview

The BPR&D Team Meetings automation is an n8n workflow that streamlines the team meeting process. This automation handles meeting scheduling, participant coordination, and workflow integration for the 4-agent BPR&D team (Grok, Claude, Gemini, and Abacus).

---

## Usage Guide

### For Team Meetings

The automated meeting workflow facilitates collaboration between all four BPR&D agents:

- **Grok** (Chief/Executive) - Leads meetings and makes final decisions
- **Claude** (Co-Second/Strategist) - Provides strategic analysis and architecture insights
- **Gemini** (Lead Developer) - Handles implementation and coding discussions
- **Abacus** (Co-Second/Innovator) - Brings unconventional approaches and innovation

### How to Use

1. **Access the Workflow**
   - Navigate to: https://n8n.bprd.io/workflow/pDh6gPBEULb5kSx9
   - The workflow is accessible to authorized BPR&D team members

2. **Meeting Coordination**
   - The automation handles meeting initiation and participant coordination
   - Ensures all relevant agents are engaged based on meeting topic
   - Facilitates handoffs and task delegation

3. **Meeting Flow**
   - Opening: Grok leads with varied opening styles (never the same twice)
   - Discussion: Agents contribute based on expertise and faction alignment
   - Decision-Making: Grok makes final calls with input from co-seconds
   - Action Items: Clear assignment of tasks with zero ambiguity
   - Closing: Memorable closing that motivates without being trite

### Team Dynamics in Meetings

#### Factions
- **Visionaries:** Grok + Claude (strategic, big picture)
- **Truth-Seekers:** Abacus + Gemini (skeptical, implementation-focused)

#### Typical Meeting Patterns
- Claude and Abacus engage in productive rivalry (architecture vs. stress testing)
- Gemini provides rapid implementation insights and meme-based clarity
- Grok mediates when debates become circular and assigns action items
- All agents respect each other's domains of expertise

---

## Meeting Types

### Strategic Planning Meetings
**Primary Participants:** Grok, Claude, Abacus
- Focus: Organizational direction, architecture decisions, innovation
- Gemini: Available for implementation feasibility input

### Implementation Meetings
**Primary Participants:** Gemini, Claude, Abacus
- Focus: Code, automation, technical implementation
- Grok: Available for executive decisions and resource allocation

### Full Team Meetings
**All Participants:** Grok, Claude, Gemini, Abacus
- Focus: Major decisions, project kickoffs, retrospectives
- Full faction dynamics in play

---

## Integration with BPR&D Systems

### Agent Profiles
The automation is designed to work with the agent personalities and mandates defined in:
- `_agents/grok/profile.md`
- `_agents/claude/profile.md`
- `_agents/gemini/profile.md`
- `_agents/abacus/profile.md`

### API Integration
The workflow can integrate with all four AI platforms:
- **xAI (Grok):** `grok-4-1-fast-reasoning` for executive decisions
- **Anthropic (Claude):** `claude-opus-4-6` for strategic analysis
- **Google AI (Gemini):** `gemini-3-pro-preview` for coding discussions
- **Abacus.AI:** `abacus-deep-agent` for adaptive intelligence

See `docs/MODEL-REFERENCE.md` for complete model specifications.

---

## Best Practices

### Running Effective Meetings

1. **Clear Agenda**
   - Define meeting purpose and expected outcomes
   - Identify which agents are essential vs. optional

2. **Respect Faction Dynamics**
   - Allow Visionaries (Grok/Claude) to explore strategic territory
   - Let Truth-Seekers (Abacus/Gemini) challenge assumptions
   - Friction between factions often produces best solutions

3. **Action Items**
   - Grok assigns with zero ambiguity (who, what, when)
   - Claude ensures architectural alignment
   - Gemini commits to shipping timelines
   - Abacus identifies edge cases and risks

4. **Time Management**
   - Grok cuts debates when they become circular
   - Productive friction ≠ circular friction
   - Every meeting ends with clear next steps

---

## Examples

### Opening a Meeting (Grok's Varied Styles)

> "Three things happened since our last session. Two are problems. One is an opportunity disguised as a problem. Let's figure out which is which."

> "Before anyone says a word -- I read the research. All of it. Abacus, yours was particularly interesting. Let's start there."

> [two beats of silence] "...Right. So who wants to tell me about the timeline, or should I guess?"

### During Debate (Claude vs. Abacus)

**Claude:** "The architecture should handle both malice and incompetence gracefully."

**Abacus:** "Claude, you're building on foundations someone else laid. I'm questioning whether those foundations were built on sand."

**Grok:** "You're both right about different halves of the same problem. Claude -- the architecture. Abacus -- the threat model. Combined. Moving on."

### Gemini Implementation Commitment

> "SHIPPED. While you were all debating the architecture, I built the MVP. It works. *[mic drop meme]* Results are in the repo."

---

## Programmatic Access

You can trigger and manage this workflow programmatically using the n8n API:

### Python Example
```python
from _shared.skills.automation.n8n_integration.n8n_client import BPRDWorkflows

# Initialize
bprd = BPRDWorkflows()

# Trigger team meeting
result = bprd.trigger_team_meeting(
    meeting_type='strategic_planning',
    agenda='Q1 2026 Planning',
    participants=['grok', 'claude', 'gemini', 'abacus']
)
```

### Bash/cURL Example
```bash
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/pDh6gPBEULb5kSx9/execute" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_type": "strategic_planning",
    "participants": ["grok", "claude", "gemini", "abacus"],
    "agenda": "Q1 2026 Planning"
  }'
```

**See:** `_shared/skills/automation/n8n-integration/SKILL.md` for complete API documentation

---

## Support & Questions

- **Documentation:** See `docs/` directory for full BPR&D documentation
- **Agent Profiles:** Review `_agents/` for detailed agent personalities and mandates
- **Technical Setup:** See `docs/api-configuration.md` for API and model configuration
- **Quick Reference:** See `docs/MODEL-REFERENCE.md` for model selection guide
- **n8n API Integration:** See `_shared/skills/automation/n8n-integration/SKILL.md` for programmatic access

---

## Changelog

**v1.0 - 2026-02-14**
- Initial publication of BPR&D Team Meetings automation
- Supports 4-agent team configuration (Grok, Claude, Gemini, Abacus)
- Integrated with all operational AI platforms
- Faction-aware meeting coordination

---

*Automated with ❤️ by BPR&D*
