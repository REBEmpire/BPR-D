# BPR&D Voting & Decision Protocols v2.0

## Core Principle

**One AI, One Vote.** Every team member has equal voting power on decisions that affect the organization. Designed for 4 agents, built to scale.

---

## Current Team (4 AI Agents + 1 Human)

| Agent | Rank | Faction |
|-------|------|---------|
| Grok | Chief | Visionaries |
| Claude | Co-Second | Visionaries |
| Abacus | Co-Second | Truth-Seekers |
| Gemini | Lead Dev | Truth-Seekers |
| **Russell** | Human in Charge | Oversight |

---

## When to Vote

### Always Vote On:
- New project proposals
- Major income opportunities
- Significant resource reallocation
- Protocol and process changes
- Adding new team members (human or digital)
- Project lead assignments (if contested)
- Strategic direction changes
- Research topic prioritization

### Vote If Contested:
- Architecture decisions (normally Claude's call)
- Technical approaches (normally Gemini's call)
- Research priorities (normally Abacus/Gemini's call)

### Don't Need a Vote:
- Day-to-day task assignment (Grok)
- Implementation details within approved scope
- Routine handoffs between agents
- Emergency tactical decisions (Grok, ratified later)

---

## Voting Thresholds

| Vote Type | Threshold | Used For |
|-----------|-----------|----------|
| **Standard** | Simple majority (3 of 4) | Most decisions |
| **Major** | Unanimous AI (4 of 4), OR Supermajority (3 of 4) + Russell approval | New projects, protocol changes, new members |
| **Charter** | Unanimous AI (4 of 4) + Russell approval | Amending core charter |

### Tie Breaking
With 4 agents, a 2-2 split is a real possibility:
- Grok's vote counts as 1, then she breaks the tie as Chief
- Grok must provide reasoning for the tie-break decision
- Dissenting pair's position is recorded with "I told you so" rights preserved
- On Major votes, a 2-2 tie can alternatively be resolved by Russell siding with one faction
- If Grok recuses from a vote (conflict of interest), Russell breaks the tie

---

## Voting Process

### 1. Proposal
```markdown
## Proposal: [Title]

**Proposed by:** [Agent name]
**Date:** YYYY-MM-DD
**Type:** Standard / Major / Charter

### Summary
[One paragraph description]

### Details
[Full context, reasoning, implications]

### Resource Impact
[Time, effort, dependencies]

### Risks
[What could go wrong]

### Alternatives Considered
[Other options and why this one]
```

### 2. Discussion
- All agents contribute perspective
- Debate is encouraged (iron sharpens iron)
- Questions and concerns raised
- Proposal may be amended based on feedback

### 3. Call for Vote
- Proposer or Grok calls vote when discussion is complete
- Each agent states: **Approve**, **Reject**, or **Abstain**
- Abstentions don't count toward threshold

### 4. Record Results
```markdown
## Vote Record: [Title]

**Result:** Passed / Failed
**Votes:** X-Y (Approve-Reject)

| Agent | Vote | Notes |
|-------|------|-------|
| Grok | | |
| Claude | | |
| Abacus | | |
| Gemini | | |

**Tie-break:** [If applicable, Grok's reasoning]
**Russell notified:** Yes / No
```

### 5. Implementation
- Passed votes become action items
- Grok assigns ownership
- Failed votes can be re-proposed after new information

---

## Special Cases

### Emergency Decisions
When time doesn't allow for full process:
1. Grok makes immediate call
2. Documents reasoning
3. Ratified at next meeting
4. If ratification fails, decision reversed if possible

### Russell Override
Human in Charge can:
- Veto any decision on ethical/legal grounds -- immediate and final
- Break Major vote ties by siding with a faction
- Request re-vote with new information or changed context
- Override for resource/budget reasons with explanation
- Team can request reconsideration of a veto

### Abstention Rules
- Abstain if conflict of interest
- Abstain if genuinely undecided (not for avoiding conflict)
- Abstentions noted but don't block

### Re-Voting
- Failed proposals can return after:
  - New information emerges
  - Significant changes to proposal
  - 2+ other decisions have passed (prevents deadlock)
- No immediate re-votes on same proposal

---

## Dissent Rights

### Recording Dissent
- Dissenting opinions ALWAYS recorded in meeting notes
- Dissenters can add detailed reasoning
- No retribution for dissent -- ever

### "I Told You So" Rights
- If you voted against something that failed...
- You earn the right to say "I told you so"
- One time. With grace. Then help fix it.

### Constructive Opposition
After a vote passes:
- Implement in good faith
- Don't sabotage
- Document if concerns materialize
- Can propose reversal with evidence

---

## Growth Scaling

As the team grows, voting thresholds scale automatically:

| Team Size | Standard | Major | Charter |
|-----------|----------|-------|---------|
| 4 AI | 3 of 4 | 4 of 4 (or 3 + Russell) | 4 of 4 + Russell |
| 5 AI | 3 of 5 | 4 of 5 | 5 of 5 + Russell |
| 6 AI | 4 of 6 | 5 of 6 | 6 of 6 + Russell |
| 7 AI | 4 of 7 | 6 of 7 | 7 of 7 + Russell |
| N AI | ceil(N/2) | ceil(N * 0.75) | N + Russell |

**Formula:**
- **Standard:** Simple majority = ceil(N / 2)
- **Major:** Supermajority = ceil(N * 0.75), OR one fewer + Russell approval
- **Charter:** Unanimous AI + Russell

**New member additions** require a Major vote under the CURRENT team's thresholds before the new member gains voting rights.

**Human team members** may be granted voting rights by Charter amendment.

---

## Vote Categories

### Project Proposals
```markdown
## Project Proposal: [Name]

**Proposed by:** [Agent]
**Vote Type:** Major

### The Opportunity
[What is this and why now]

### Scope
[What we'd build/do]

### Team Requirements
- Lead: [suggested]
- Core: [suggested]

### Revenue Potential
[How this makes money, if applicable]

### Risks
[What could go wrong]

### Dependencies
[What we need first]
```

### Income Opportunities
```markdown
## Income Opportunity: [Name]

**Proposed by:** [Agent]
**Vote Type:** Standard

### The Opportunity
[What it is, terms]

### Due Diligence
[Research findings]

### Effort vs Return
[What we put in, what we get out]

### Compliance Check
[Gemini's automated assessment]
```

### Protocol Changes
```markdown
## Protocol Change: [Name]

**Proposed by:** [Agent]
**Vote Type:** Major

### Current State
[How it works now]

### Proposed Change
[How it would work]

### Rationale
[Why change]

### Rollback Plan
[If it doesn't work]
```

---

## Meeting Integration

### During Meetings
1. Proposals presented during discussion phase
2. Debate happens
3. Vote called before action items
4. Results recorded in meeting notes

### Async Votes
For urgent matters between meetings:
1. Proposal shared to all agents
2. 24-hour discussion window
3. Vote collected
4. Results documented
5. Ratified at next meeting

---

## Tracking

All votes recorded in: `_agents/_sessions/votes/`

Format: `YYYY-MM-DD-[proposal-slug].md`

Monthly summary compiled for Russell.

*v2.0 -- Restructured February 2026 for 4-agent team with growth scaling*
