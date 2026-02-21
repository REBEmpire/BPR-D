# Meeting-Code-Deployer (MCD)

**Version:** 2.0.0  
**Author:** Abacus (System Architecture)  
**Status:** Active

---

## Overview

The Meeting-Code-Deployer is an automated pipeline that transforms meeting discussions into deployed code changes, tasks, and documentation. It ensures no action item falls through the cracks.

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐
│   Meeting   │────▶│  Transcript  │────▶│  Action   │────▶│  Tasks   │
│   (Live)    │     │  (Parsed)    │     │  Items    │     │  & Code  │
└─────────────┘     └──────────────┘     └───────────┘     └──────────┘
```

---

## Quick Start

### Basic Usage

```bash
# Navigate to repository root
cd /path/to/BPR-D

# Dry run (preview what would be created)
python scripts/meeting-code-deployer.py meetings/logs/sample-meeting.md --dry-run

# Process and create files
python scripts/meeting-code-deployer.py meetings/logs/sample-meeting.md

# Process and auto-commit
python scripts/meeting-code-deployer.py meetings/logs/sample-meeting.md --auto-commit
```

### Sample Test Run

```bash
# Test with included sample meeting
python scripts/meeting-code-deployer.py meetings/logs/sample-meeting-for-testing.md --dry-run
```

---

## Features

### 1. Transcript Parsing
- Extracts action items from meeting transcripts
- Identifies decisions made during meetings
- Captures code snippets with language detection
- Parses YAML frontmatter for meeting metadata

### 2. Skill-Web Integration
- Links extracted items to skill-web nodes in `_shared/skill-graphs/bprd-core/`
- Suggests appropriate owners based on skill matching
- Identifies skill gaps for escalation

### 3. Task Creation
- Creates v2-compliant task files in `tasks/` directory
- Generates proper task IDs (BPRD-YYYY-NNNN format)
- Includes verification criteria
- Updates `BPR&D_To_Do_List.md`

### 4. Documentation Generation
- Meeting summary documents
- Action item documentation
- Skill gap analysis reports

---

## CLI Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without creating files |
| `--auto-commit` | Automatically commit changes |
| `--create-pr` | Create a PR (requires `--auto-commit`) |
| `--config PATH` | Custom config file path |
| `--output PATH` | Custom report output path |
| `--format markdown\|json` | Report format (default: markdown) |
| `--quiet` | Suppress progress output |
| `--version` | Show version |

---

## Configuration

### Config File: `config.yaml`

```yaml
mcd:
  paths:
    skill_web: "_shared/skill-graphs/bprd-core"
    tasks_dir: "tasks"
    meetings_dir: "meetings/logs"
    todo_list: "BPR&D_To_Do_List.md"
    counter_file: "tasks/_counter.yaml"
  
  extraction:
    min_confidence: 0.7
    auto_assign: true
    skill_matching: true
    action_patterns:
      - "will implement"
      - "will create"
      - "TODO:"
      - "ACTION:"
      # ...
  
  agents:
    - name: "claude"
      skills: ["code-review", "api-development"]
    - name: "abacus"
      skills: ["system-architecture", "automation"]
    # ...
```

### Action Detection Patterns

The parser recognizes action items through:

1. **Explicit assignments**: `@claude will implement...`
2. **Commitment language**: `I'll do...`, `Let's make sure...`
3. **Decision outcomes**: `We decided to...`
4. **Action markers**: `TODO:`, `ACTION:`, `TASK:`
5. **Deadline mentions**: `by Friday`, `by end of week`

---

## Module Structure

```
_agents/meeting-code-deployer/
├── __init__.py          # Package initialization
├── config.yaml          # Configuration file
├── deployer.py          # Main orchestrator
├── parser.py            # Transcript parsing
├── skill_linker.py      # Skill-web integration
├── code_generator.py    # File generation
├── task_creator.py      # Task file creation
└── README.md            # This file
```

### Component Responsibilities

| Module | Purpose |
|--------|----------|
| `deployer.py` | Orchestrates the full pipeline |
| `parser.py` | Parses transcripts, extracts action items/decisions/code |
| `skill_linker.py` | Links items to skill-web nodes, suggests owners |
| `code_generator.py` | Generates documentation and code files |
| `task_creator.py` | Creates v2 task files, updates to-do list |

---

## Meeting Transcript Format

### Recommended Structure

```markdown
---
meeting_id: meeting-2026-02-21-14-00-topic
date: 2026-02-21
time: "14:00"
duration_minutes: 45
participants:
  - name: "Grok"
    role: facilitator
  - name: "Claude"
    role: attendee
topics_discussed:
  - "Feature implementation"
  - "Bug fixes"
---

# Meeting Title

## Discussion

**Speaker:** Content of discussion...

@agent will implement feature by deadline.

TODO: Create documentation for new API.

DECISION: We will use approach X for implementation.

```python
# Code snippets are captured
def example():
    pass
```

## Action Items Summary

1. Agent - Task description
```

---

## Output Files

### Task Files

- Location: `tasks/backlog/` or `tasks/active/`
- Format: `BPRD-YYYY-NNNN.md`

### Meeting Summary

- Location: `meetings/summaries/`
- Format: `{meeting_id}-summary.md`

### Deployment Report

- Location: `meetings/reports/`
- Format: `{meeting_id}-deployment-report.md`

---

## Integration Points

### Skill-Web (`_shared/skill-graphs/bprd-core/`)

- MOC files for navigation
- Skill nodes for capability matching
- Agent hooks for assignment

### Task System (`tasks/`)

- Task ID counter in `_counter.yaml`
- Status directories: `backlog/`, `active/`, `review/`, `completed/`
- Format follows v2 work-item protocol

### To-Do List (`BPR&D_To_Do_List.md`)

- Auto-updated with new tasks
- Maintains v2 format

---

## Error Handling

| Error | Resolution |
|-------|------------|
| Transcript not found | Check file path |
| No actions extracted | Meeting marked informational |
| Skill match failed | Task created with skill_gap flag |
| Low confidence | Warning logged, item skipped |

---

## Examples

### Example 1: Dry Run

```bash
python scripts/meeting-code-deployer.py \
    meetings/logs/sprint-planning-2026-02-21.md \
    --dry-run
```

Output:
```
============================================================
  🚀 Meeting-Code-Deployer v2.0.0
============================================================

  Transcript: meetings/logs/sprint-planning-2026-02-21.md
  Mode: DRY RUN

------------------------------------------------------------

📄 Parsing transcript: meetings/logs/sprint-planning-2026-02-21.md
   Found: 5 actions, 2 decisions, 1 code snippets
🔗 Linking to skill-web nodes...
   Linked: 4, Gaps: 1
📝 Creating task files...
   Created: 5 tasks
📁 Generating files...
   Generated: 2 files
📋 Updating To-Do List...
   [DRY RUN] Would add 5 tasks to BPR&D To-Do List
✅ Dry run complete!
```

### Example 2: Full Deployment

```bash
python scripts/meeting-code-deployer.py \
    meetings/logs/sprint-planning-2026-02-21.md \
    --auto-commit \
    --output meetings/reports/sprint-report.md
```

---

## Troubleshooting

### "No action items extracted"

- Ensure transcript uses recognized action patterns
- Add `TODO:`, `ACTION:`, or `@agent will` markers
- Check `min_confidence` setting in config

### "Skill match failed"

- Verify skill-web nodes exist in `_shared/skill-graphs/bprd-core/`
- Add relevant keywords to skill node files
- Check agent skills configuration

### "Task ID counter error"

- Ensure `tasks/_counter.yaml` exists and is valid YAML
- Check file permissions

---

## Related Documentation

- [V2 Architecture](../../docs/v2-architecture/README.md)
- [Work Item Protocol](../../docs/v2-architecture/work-item-protocol.md)
- [Meeting-Code-Deployer Spec](../../docs/v2-architecture/meeting-code-deployer.md)
- [Skill-Web Integration](../../docs/v2-architecture/skill-web-integration.md)

---

*Part of BPR&D V2 Architecture - Meeting-to-Code Pipeline*
