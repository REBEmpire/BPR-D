# Agent Memory Guide v1.0

This guide explains how to use the team's shared memory system effectively.

## 🧠 Memory Types

### 1. Episodic (Session Logs)
**Location:** `_agents/_shared/memories/episodic/YYYY/MM/`
**Template:** `_agents/_templates/episodic_memory.md`
**When to use:** At the end of every significant session.
**Purpose:** Capture *what happened*, the mood, key interactions, and the story of the session.

### 2. Semantic (Knowledge Base)
**Location:** `_agents/_shared/memories/semantic/`
**When to use:** When you learn a new fact about the domain (e.g., how the Abacus API handles errors).
**Purpose:** Shared textbook knowledge that all agents can reference.

### 3. Procedural (How-To)
**Location:** `_agents/_shared/memories/procedural/`
**When to use:** When you discover a technique that works well (e.g., a specific prompting strategy).
**Purpose:** Muscle memory for the team.

### 4. Strategic (Decisions)
**Location:** `_agents/_shared/memories/strategic/`
**Template:** `_agents/_templates/decision_record.md`
**When to use:** When a major architectural or project decision is made.
**Purpose:** Prevent re-litigating settled debates.

## 🤝 Collective Memory

### Team State
**Location:** `_agents/team_state.md`
**Owner:** Grok (or current Session Leader)
**Purpose:** The single source of truth for the *current* focus. Read this first!
**Action:** Update this file if the team's priorities shift or a milestone is reached.

### User Context
**Location:** `_agents/_shared/user_context.md`
**Owner:** Russell (The User)
**Purpose:** Direct instructions and preferences from the human lead.
**Action:** Respect these constraints absolutely.

## 🛠 Using Templates

All templates are stored in `_agents/_templates/`.
- **Handoffs:** Use `handoff.md` when delegating tasks.
- **Meetings:** Use `meeting_notes.md` to record formal syncs.
- **Learnings:** Use `learnings.md` when you have an "Aha!" moment.

## 🚀 Best Practices

1.  **Read First:** Always check `team_state.md` and relevant memory folders before starting work.
2.  **Write Often:** Don't rely on implicit context. If it's not written down, it didn't happen.
3.  **Cross-Reference:** Link to related files using relative paths.
4.  **Stay in Character:** Even memory files should reflect your persona (within reason).
