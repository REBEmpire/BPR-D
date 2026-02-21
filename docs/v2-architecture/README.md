# BPR&D V2 Architecture

**Version:** 2.0.0  
**Effective Date:** 2026-02-21  
**Status:** Active

---

## Overview

The V2 Architecture addresses critical issues identified in the current BPR&D system:
- Massive file duplication (182 handoff files reduced to single source)
- Phantom task problem (tasks without verification)
- Underutilized skill-web system
- Unclear agent ownership boundaries

---

## V2 Directory Structure

### Single Source of Truth Principle

Every file type has **ONE canonical location**. Duplicates are prohibited.

```
BPR-D/
├── _agents/                    # Agent-specific configurations
│   ├── {agent-name}/           # Per-agent directory
│   │   ├── profile.md          # Agent capabilities & role
│   │   ├── context/            # Agent-specific context (read-only)
│   │   └── sessions/           # Active session states
│   └── _registry.yaml          # Master agent registry
│
├── _handoffs/                  # SINGLE handoff location (moved from _agents/_handoffs)
│   ├── active/                 # Currently active handoffs
│   ├── archived/               # Completed/cancelled handoffs
│   └── _index.yaml             # Handoff registry
│
├── _shared/                    # Shared resources (single location)
│   ├── skills/                 # Skill definitions
│   ├── skill-web/              # Skill graph & relationships
│   ├── templates/              # Document templates
│   ├── knowledge/              # Shared knowledge base
│   └── memories/               # Persistent memories
│
├── docs/                       # Documentation
│   ├── v2-architecture/        # V2 system docs (this directory)
│   └── guides/                 # User & developer guides
│
├── meetings/                   # Meeting management
│   ├── transcripts/            # Raw transcripts (canonical)
│   ├── action-items/           # Extracted action items
│   └── summaries/              # Meeting summaries
│
├── research/                   # Research outputs
│   ├── {topic}/                # Topic-specific research
│   │   ├── sources/            # Raw sources
│   │   ├── briefs/             # Research briefs
│   │   └── reports/            # Final reports
│   └── _index.yaml             # Research topic registry
│
├── scripts/                    # Automation scripts
│   ├── v2-migration/           # Migration tools
│   └── automation/             # Runtime automation
│
├── tasks/                      # Task management
│   ├── backlog/                # Unassigned tasks
│   ├── active/                 # In-progress tasks
│   ├── review/                 # Tasks pending verification
│   └── completed/              # Verified complete tasks
│
└── BPR&D-To-Do-List.md         # Master task list (single source)
```

---

## File Naming Conventions

### Enforcement Rules

All files MUST follow these patterns. Pre-commit hooks enforce compliance.

| File Type | Pattern | Example |
|-----------|---------|--------|
| Task Files | `BPRD-{YYYY}-{NNNN}.md` | `BPRD-2026-0042.md` |
| Handoffs | `handoff-{agent}-{task-id}-{YYYYMMDD}.md` | `handoff-grok-BPRD-2026-0042-20260221.md` |
| Meeting Transcripts | `meeting-{YYYY-MM-DD}-{HH-MM}-{topic}.md` | `meeting-2026-02-21-14-30-sprint-planning.md` |
| Action Items | `action-{meeting-id}-{NNN}.md` | `action-2026-02-21-14-30-001.md` |
| Research Briefs | `brief-{topic}-{YYYY-MM-DD}.md` | `brief-epstein-2026-02-21.md` |
| Agent Profiles | `profile.md` (in agent directory) | `_agents/grok/profile.md` |
| Session States | `session-{YYYY-MM-DD}-{agent}.yaml` | `session-2026-02-21-abacus.yaml` |

### Prohibited Patterns

- Timestamps in filenames (e.g., `file_063331.md`) - **BLOCKED**
- Duplicate content anywhere - **BLOCKED**
- Files outside canonical locations - **BLOCKED**
- Random suffixes (e.g., `file-copy.md`, `file (2).md`) - **BLOCKED**

---

## Agent Responsibility Matrix

### Core Principle: No Overlaps

Each responsibility has **ONE owner**. Cross-functional work requires explicit handoffs.

| Domain | Owner | Responsibilities | Cannot Touch |
|--------|-------|------------------|---------------|
| **System Architecture** | Abacus | V2 design, automation, migrations | Content creation, research decisions |
| **Strategic Direction** | Grok | Vision, priorities, major decisions | Code implementation, file organization |
| **Research Operations** | Claude | Analysis, briefs, fact-checking | Publishing, financial tracking |
| **Content Production** | Gemini | Writing, editing, media generation | System architecture, research methodology |
| **Task Verification** | Perplexity | Completion validation, quality audits | Task creation, priority setting |
| **Code Deployment** | GitHub Bot | CI/CD, deployments, testing | Content, research, meetings |

### Handoff Requirements

When work crosses domains:
1. Owner creates handoff document in `_handoffs/active/`
2. Receiving agent must acknowledge within 4 hours
3. Original owner tracks until verified complete
4. Only Perplexity can mark tasks as `Verified`

---

## Integration Points

### Linked Documents

- [Work Item Protocol](./work-item-protocol.md) - Task ID system and status workflow
- [Meeting-Code-Deployer](./meeting-code-deployer.md) - Meeting to code pipeline
- [Skill-Web Integration](./skill-web-integration.md) - Skill graph runtime integration
- [Handoff Protocol v2](./handoff-protocol-v2.md) - Agent handoff lifecycle

### Automation Scripts

- [`scripts/v2-migration/cleanup.py`](../../scripts/v2-migration/cleanup.py) - Duplicate removal & consolidation
- [`scripts/v2-migration/pre-commit-check.sh`](../../scripts/v2-migration/pre-commit-check.sh) - Convention enforcement

---

## Migration Path

### Phase 1: Cleanup (Week 1)
1. Run `cleanup.py` to remove duplicates
2. Consolidate handoffs to `_handoffs/`
3. Install pre-commit hooks

### Phase 2: Task Migration (Week 2)
1. Assign task IDs to existing items
2. Link tasks to skill-web nodes
3. Add verification criteria

### Phase 3: Automation (Week 3)
1. Deploy Meeting-Code-Deployer
2. Enable runtime skill injection
3. Activate status synchronization

---

## Changelog

| Version | Date | Changes |
|---------|------|--------|
| 2.0.0 | 2026-02-21 | Initial V2 architecture |
