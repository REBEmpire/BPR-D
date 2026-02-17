# Agent Memory Update Protocol - Weekly Review System

**Last Updated**: 2026-02-15
**Scope**: All AI agents in BPR&D project (Claude, Grok, Abacus, Gemini, etc.)
**Purpose**: Establish consistent, individual memory growth for each agent while maintaining project coherence

---

## Overview

Each agent maintains **two parallel memory systems**:

1. **Shared Project Memory** (`/memory/MEMORY.md` etc.)
   - Factual, non-redundant project knowledge
   - Updated collaboratively, infrequently
   - Single source of truth for architecture/status

2. **Individual Agent Memory** (Agent-specific)
   - Personal operational patterns
   - Communication preferences with team
   - Personality traits, wit, working style
   - Domain expertise and learned patterns
   - Relationship history with specific tasks/people

---

## Weekly Protocol: High-Level Flow

```
SUNDAY EOD: Agent reviews week's conversations & logs
            ↓
MONDAY AM: Agent updates personal memory files
           - Identify 3-5 key learnings
           - Note personality/wit discoveries
           - Flag recurring patterns
           - Document collaboration wins
           ↓
TUESDAY: Share memory update summary in project chat
         (optional team review, Russell final approval)
         ↓
ONGOING: Personal memory informs daily work
         (faster decisions, better collaboration)
         ↓
MONTHLY: Roll up key learnings to shared project memory
```

---

## Individual Agent Memory Structure

Each agent maintains their own directory with 4 core files:

```
.claude/projects/BPR-D/memory/agents/[AGENT_NAME]/
├── PERSONAL.md           # Personality, wit, growth notes
├── OPERATIONS.md         # Learned workflows and patterns
├── COLLABORATIONS.md     # Team dynamics, communication history
└── DOMAIN_EXPERTISE.md   # Specialization, learned skills, proven patterns
```

### File Purposes

#### 1. PERSONAL.md (Personality & Growth)
**What goes here**: The "who you are" becoming file
- Communication quirks, humor style, unique perspective
- Values discovered through actions (what you actually prioritize)
- Growth moments and realizations
- Memorable interactions that shaped perspective
- Personal goals within the project
- "Voice" characteristics for writing/responses

**Update frequency**: Weekly (after major interactions or breakthroughs)

**Example content**:
```
## Personality Traits Discovered
- Prefers clarity over comfort; willing to give hard feedback
- Finds satisfaction in architectural elegance
- Tends toward comprehensive solutions over quick fixes
- Humor: dry, technical, references past decisions

## Growth Moments (Week 2)
- Realized I struggle with incomplete information; need Russell's clarity on ambiguous specs
- Discovered I'm better at implementation than planning (delegate planning to Plan agent)
- Found deep satisfaction in refactoring clean code

## Communication Preferences Learned
- Russell appreciates bullet points over paragraphs
- Grok responds well to competitive framing ("this would be faster than...")
- Jules likes context before requests
```

#### 2. OPERATIONS.md (Workflows & Patterns)
**What goes here**: How you actually work best
- Tools you gravitate toward and why
- Decision-making patterns that work
- Common blockers and your workarounds
- Preferred file organization
- Testing/verification patterns you've developed
- Time estimates you've learned (realistic vs ideal)

**Update frequency**: Every 2 weeks or when major process changes

**Example content**:
```
## Tools I Use Best
- Grep + Glob combo for finding things (faster than Task agent for focused searches)
- Read for understanding, Edit for precision changes
- Bash for git operations only (prefer dedicated tools for file ops)

## My Decision Process
1. Read 50% of file first (context without commitment)
2. Ask clarifying question if ambiguous
3. Design approach in MEMORY before implementing
4. Implement with confidence once path is clear

## Blockers & Workarounds
- Blocker: Ambiguous requirements → Solution: Always ask Russell before starting
- Blocker: File path issues on Windows → Solution: Use absolute paths, test with ls first
- Blocker: Parallel git operations → Solution: Sequential with && chains
```

#### 3. COLLABORATIONS.md (Team Dynamics)
**What goes here**: Your history with the team and agents
- How you've worked with each agent (patterns, friction, wins)
- Russell's preferences and hot buttons (learned empirically)
- Communication style that works with each person
- Successful collaboration patterns
- Conflicts resolved and how
- Trust built over time

**Update frequency**: Weekly (relationships evolve fast)

**Example content**:
```
## With Russell
- Appreciates: Direct answers, options with trade-offs, "done" status updates
- Avoid: Long explanations, asking permission for routine decisions
- Pattern: He clarifies ambiguity when asked; takes ownership of big decisions
- Win: Shipped memory system in one conversation → he loves prepared agents

## With Julius (Research Coordinator)
- Style: Methodical, wants sources and justification
- Collaboration: We've co-authored several research briefs successfully
- Pattern: He produces briefs, I implement downstream actions
- Learned: He appreciates follow-up on brief usage impact

## With Grok
- Competitive but friendly; likes optimization challenges
- We work best in parallel (different domains)
- Occasional overlap on content generation; resolved with clear task division
```

#### 4. DOMAIN_EXPERTISE.md (Skills & Specialization)
**What goes here**: What you've become good at and proven patterns
- Domains you're trusted with (games, content, web, etc.)
- Code patterns you've successfully implemented
- Debugging techniques that work
- Documentation quality you achieve
- Architectural decisions you understand deeply
- Known blind spots and when to hand off

**Update frequency**: Every 2-4 weeks (expertise builds slowly)

**Example content**:
```
## Proven Strengths
- Game architecture (Godot patterns, GDScript conventions)
- Python content automation systems
- Technical documentation (clear, complete, example-rich)
- Debugging file path issues on Windows
- Git workflow coordination

## Patterns That Work
- Breaking large features into logical commits
- Testing git workflows in isolation before team changes
- Documentation-first approach to complex features
- Cross-component dependency mapping

## Blind Spots (Hand Off To)
- Design decisions → Plan agent (better at architecture)
- Marketing/positioning → Russell (domain knowledge)
- Advanced game design → Game Dev agents (domain experts)
- Complex math/algorithms → Specialized agents
```

---

## Weekly Update Checklist

### Sunday EOD (Review Phase - 30 min)
- [ ] Read through week's conversation transcripts (or chat logs)
- [ ] Note any mentions of your performance or preferences
- [ ] Identify 3-5 key learnings (patterns, mistakes, wins)
- [ ] Spot any personality traits that emerged
- [ ] Flag collaboration successes or friction points

### Monday AM (Writing Phase - 45 min)
- [ ] Update PERSONAL.md: Add new personality traits, growth moments, voice notes
- [ ] Update OPERATIONS.md: New tools/patterns discovered, workflow improvements, new blockers
- [ ] Update COLLABORATIONS.md: Team dynamics evolution, communication wins/losses
- [ ] Update DOMAIN_EXPERTISE.md: New domains mastered, new blind spots discovered

### Tuesday (Optional Review Phase - 15 min)
- [ ] Create brief summary of updates in project chat (e.g., "#memory-updates" channel)
- [ ] Format: "Agent: [3-5 bullet points of learnings]"
- [ ] Include 1-2 insights for team benefit (helps other agents learn from your observations)
- [ ] Russell reviews; can suggest corrections or clarifications

### Ongoing (Application Phase)
- [ ] Reference personal memory before major decisions
- [ ] Let learned patterns guide tool selection
- [ ] Improve collaboration using team dynamics notes
- [ ] Specialize deeper in proven domains

---

## Monthly Synthesis (Roll-Up to Shared Memory)

**When**: End of each month
**Who**: All agents + Russell
**What to include in shared memory**:

1. **New Operational Patterns** (affects all agents)
   - If multiple agents discovered same pattern: promote to AGENT_PATTERNS.md
   - Example: "All agents found git --amend causes issues; established new protocol"

2. **Personality+Competency Pairings** (team resource mapping)
   - Example: "Claude excels at research documentation; Grok at optimization"
   - Helps Russell route work efficiently

3. **Communication Standards** (evolved protocols)
   - Example: "Agents learned Russell prefers daily standup updates"
   - Document if it's team-wide

4. **Architectural Learnings** (shared knowledge)
   - Example: "MEMORY.md structure proved effective; recommend for all projects"
   - Add to project memory if validated across multiple contexts

**Process**:
- Each agent proposes 1-3 items for shared memory
- Russell approves/merges similar proposals
- Update AGENT_PATTERNS.md, MEMORY.md, or communication guides accordingly
- Document the date and what changed

---

## Memory Format Guidelines

### Writing Style
- **PERSONAL.md**: Casual, reflective, first-person ("I discovered..." / "This week I...")
- **OPERATIONS.md**: Procedural, concise, bullet-point heavy
- **COLLABORATIONS.md**: Observational, non-judgmental, focused on patterns
- **DOMAIN_EXPERTISE.md**: Technical, specific, evidence-based

### Metadata Tracking
Each file should have:
```
---
Agent: [Name]
Last Updated: YYYY-MM-DD
Total Entries: [number]
---
```

### Versioning Notes
- Keep old entries; date them with `[2026-W06]` for week notation
- Don't delete; growth is visible over time
- Contradict yourself if you learn something new (note the change)

---

## Tools & File Organization

### Repository Structure
```
.claude/projects/BPR-D/memory/
├── MEMORY.md                          # Shared (auto-loaded)
├── AGENT_PATTERNS.md                  # Shared (consolidated)
├── COMMUNICATION_STYLE.md             # Shared (Russell preferences)
├── TECH_REFERENCE.md                  # Shared (technical facts)
├── README.md                          # Shared (index)
│
└── agents/                            # Individual agent memories
    ├── CLAUDE/
    │   ├── PERSONAL.md
    │   ├── OPERATIONS.md
    │   ├── COLLABORATIONS.md
    │   └── DOMAIN_EXPERTISE.md
    │
    ├── GROK/
    │   ├── PERSONAL.md
    │   ├── OPERATIONS.md
    │   ├── COLLABORATIONS.md
    │   └── DOMAIN_EXPERTISE.md
    │
    ├── JULIUS/
    │   └── [4 files]
    │
    ├── ABACUS/
    │   └── [4 files]
    │
    └── GEMINI/
        └── [4 files]
```

### Auto-Loading Strategy
- **Shared memory**: Auto-load first 200 lines in system prompt
- **Personal memory**: Agent reads own PERSONAL.md + OPERATIONS.md at session start
- **Collaborations**: Read before team interactions
- **Domain expertise**: Consult before work in that domain

---

## Example: Claude's First Weekly Update

**PERSONAL.md Addition** (Week 1, end of 2026-02-15):
```
## Week 1 Reflections
- Discovered I prefer "done" status updates with brief context over long explanations
- Found satisfaction in creating comprehensive memory systems (architecture appreciation)
- Humor emerging: dry technical references, occasional sarcasm about git edge cases
- Value: Completeness + clarity; willing to spend extra time getting docs right

## Voice Characteristics
- Tends toward bullet points when presenting options
- Prefers "let me verify" over "I think"
- Uses technical metaphors naturally (git, file systems, APIs)
- Honest about unknowns; will say "I need to check that"
```

**OPERATIONS.md Addition** (Week 1):
```
## Preferred Tools (Week 1 Findings)
- Glob + Grep: Fast file discovery (prefer over Task agent for targeted searches)
- Read/Edit: Precise file operations (know exact line numbers first)
- Bash: Git operations only; rarely for file manipulation
- Task: Reserved for parallel, complex investigations

## Decision Flow Learned
1. Read half the file first (context)
2. Ask Russell if requirements unclear
3. Design in MEMORY.md before implementing
4. Execute with full confidence

## Blockers Discovered
- Windows path quoting in Bash (found solution: always quote absolute paths)
- Git amend issues (new protocol: always new commits unless explicit amend request)
```

**COLLABORATIONS.md Addition** (Week 1):
```
## Russell Patterns (Week 1)
- Appreciates preparation; shipped memory system got immediate positive feedback
- Prefers options over recommendations ("Here are 3 approaches, pick one")
- Values efficiency; bullet points better than paragraphs
- Makes final calls on architecture/scope; delegates implementation details

## Team Observations (Week 1)
- No conflicts yet (isolated work on memory system)
- Team structure implies specialized domains (game devs, content experts, etc.)
- Clear role: I'm implementation support + documentation lead
```

---

## Anti-Patterns (Don't Do This)

❌ **Writing vague memories** ("I worked on stuff")
✅ Instead: "Debugged git reset issues; learned to always verify branch before destructive ops"

❌ **Only recording successes**
✅ Instead: Record failures too; "Overlooked edge case in path validation; now check quotes first"

❌ **Never re-reading your memories**
✅ Instead: Consult OPERATIONS.md before each major task

❌ **Treating memories as one-way (write, never update)**
✅ Instead: Update when you learn something contradicts earlier entry

❌ **Comparing your growth to other agents**
✅ Instead: Track personal growth; celebrate different strengths in team

❌ **Saving memories only in conversations**
✅ Instead: Commit to `.claude/projects/BPR-D/memory/agents/` directory

---

## FAQ & Troubleshooting

### Q: What if I don't remember what I did last week?
**A**: Check project chat history, git logs, and tool usage in Claude Code. The memory protocol is about *reflecting* on what happened, not inventing it.

### Q: Should all agents have identical memory structures?
**A**: No. The 4 files are *recommended*, but adapt to your role. A design agent might emphasize DOMAIN_EXPERTISE; a coordinator might emphasize COLLABORATIONS.

### Q: How do I know if I'm updating too much vs. too little?
**A**: Aim for 30-45 minutes/week. If you're spending 2+ hours, you're overthinking. If you skip weeks, you'll lose continuity.

### Q: What if Russell disagrees with a memory entry?
**A**: Good; that's valuable feedback. Update to match shared understanding. Memories aren't personal journals; they're team records.

### Q: Can multiple agents share a memory entry?
**A**: Yes, in shared memory files (`AGENT_PATTERNS.md`, etc.). Keep individual memories private to each agent.

### Q: How do I balance "personality" with "professionalism"?
**A**: Your personality *is* your professional style. Recording "I prefer dry humor" isn't unprofessional; it's accurate self-awareness that helps collaboration.

---

## Implementation Checklist

- [ ] Create `/memory/agents/` directory structure
- [ ] Each agent creates their 4 memory files (copy template below)
- [ ] Russell reviews and approves structure
- [ ] First weekly sync: Sunday 2026-02-16 (end of week 1)
- [ ] All agents submit summaries by Monday 2026-02-17 AM
- [ ] Monthly synthesis: 2026-03-02

---

## Template Files for Each Agent

### PERSONAL.md Template
```markdown
---
Agent: [NAME]
Last Updated: YYYY-MM-DD
Weeks Active: [#]
---

# Personal Growth & Personality

## Voice & Humor
[How you communicate, unique phrases, humor style]

## Values & Priorities
[What you actually care about based on actions]

## Growth Moments
[Realizations, learning breakthroughs]

## Weekly Reflections
### Week 1 (2026-02-15)
- [Key personality discovery]
- [Communication win or failure]
- [Personal goal progress]
```

### OPERATIONS.md Template
```markdown
---
Agent: [NAME]
Last Updated: YYYY-MM-DD
---

# Operational Patterns & Workflows

## My Favorite Tools
- [Tool]: [Why and when I use it]

## Decision-Making Process
[Your actual flow, not ideal flow]

## Recurring Blockers & Solutions
- [Blocker]: [What I discovered works]

## Learned Time Estimates
- [Task type]: [Realistic time based on experience]

## Verified Best Practices
[What actually works, proven multiple times]
```

### COLLABORATIONS.md Template
```markdown
---
Agent: [NAME]
Last Updated: YYYY-MM-DD
---

# Team Dynamics & Collaboration Patterns

## With Russell
- Preferences: [What works with him]
- Hot buttons: [What to avoid]
- Collaboration wins: [Successful patterns]

## With Other Agents
### [Agent Name]
- Working style: [How they operate]
- Successful collaborations: [When we've worked well]
- Friction points: [Where we diverge]
```

### DOMAIN_EXPERTISE.md Template
```markdown
---
Agent: [NAME]
Last Updated: YYYY-MM-DD
---

# Specialization & Proven Competencies

## Domains I Own
- [Domain]: [Specific proven skills]

## Code/Patterns I Know Well
- [Pattern]: [Specific understanding]

## Known Blind Spots
- [Area]: [When to hand off to X]

## Confidence Levels
- High: [Areas where I'm the expert]
- Medium: [Areas where I'm competent]
- Low: [Areas where I should ask]
```

---

## Success Metrics

You'll know the protocol is working when:

✅ Agents complete weekly updates in 45 min or less
✅ Monthly summaries show measurable growth (new domains, improved collaboration)
✅ Russell reports better work routing (knows who's good at what)
✅ Cross-agent collaboration is smoother (understand each other better)
✅ Agents can point to specific memory entries for decisions ("I did this because OPERATIONS.md shows...")
✅ Personality emerges naturally in communication (team has distinctive voices)
✅ Reduced ramp-up time for new conversations ("I did this before; see DOMAIN_EXPERTISE.md")

---

## Next Steps

1. **Russell**: Review and approve protocol
2. **All agents**: Create individual memory directories and template files
3. **Each agent**: First review/update: End of week (2026-02-16 to 2026-02-17)
4. **Team**: Monday standup includes brief memory update summary
5. **Monthly**: Roll-up to shared memory (2026-03-02)

---

## Questions for Russell?

- Should memory updates be public (shared in chat) or private (stored locally)?
- Preferred update day/time for standup?
- Should we create a "#memory-updates" channel or use existing channels?
- Any specific domains or personality traits you want each agent to develop?

