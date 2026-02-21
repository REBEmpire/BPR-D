# Work Item Tracking Protocol v2

**Version:** 2.0.0  
**Effective Date:** 2026-02-21  
**Owner:** Abacus (System Architecture)

---

## Task ID System

### Format: `BPRD-{YYYY}-{NNNN}`

| Component | Description | Example |
|-----------|-------------|--------|
| `BPRD` | Fixed prefix for BPR&D tasks | `BPRD` |
| `YYYY` | Year of creation | `2026` |
| `NNNN` | Sequential 4-digit number | `0001` |

**Full Example:** `BPRD-2026-0042`

### ID Generation Rules

1. IDs are **immutable** once assigned
2. Deleted tasks retain their ID (never reused)
3. Sequential counter stored in `tasks/_counter.yaml`
4. Only automation scripts can generate new IDs

---

## Required Fields

Every work item MUST include:

```yaml
---
id: BPRD-2026-0042                              # REQUIRED: Unique task ID
source: meetings/transcripts/meeting-2026-02-21-14-30-sprint-planning.md#L45
                                                # REQUIRED: Origin (meeting transcript link)
skill_web_node: skills/code-review              # REQUIRED: Linked skill-web node
owner: claude                                   # REQUIRED: Assigned agent
status: Created                                 # REQUIRED: Current status
created_at: 2026-02-21T14:35:00Z               # REQUIRED: ISO 8601 timestamp
updated_at: 2026-02-21T14:35:00Z               # REQUIRED: Last update time

# Verification (REQUIRED for completion)
verification_criteria:
  - "Code passes all unit tests"
  - "Documentation updated"
  - "PR merged to main branch"
verified_by: null                               # Set when verified
verified_at: null                               # Set when verified
---
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique task identifier |
| `source` | string | ✅ | Meeting transcript link with line number |
| `skill_web_node` | string | ✅ | Path to skill node in skill-web |
| `owner` | string | ✅ | Assigned agent (from registry) |
| `status` | enum | ✅ | Current workflow status |
| `created_at` | datetime | ✅ | Creation timestamp |
| `updated_at` | datetime | ✅ | Last modification time |
| `verification_criteria` | array | ✅ | Checkable completion criteria |
| `verified_by` | string | ❌ | Agent who verified completion |
| `verified_at` | datetime | ❌ | Verification timestamp |
| `priority` | enum | ❌ | `critical`, `high`, `medium`, `low` |
| `due_date` | date | ❌ | Target completion date |
| `dependencies` | array | ❌ | IDs of blocking tasks |
| `related_handoffs` | array | ❌ | Links to handoff documents |

---

## Status Workflow

### States

```
┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌────────┐    ┌──────────┐    ┌──────────┐
│ Created  │───▶│ Assigned │───▶│ In-Progress │───▶│ Review │───▶│ Verified │───▶│ Complete │
└──────────┘    └──────────┘    └─────────────┘    └────────┘    └──────────┘    └──────────┘
      │               │                │                │              │
      │               │                │                │              │
      ▼               ▼                ▼                ▼              │
┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌────────┐         │
│ Blocked  │◀───│ Blocked  │◀───│   Blocked   │◀───│ Failed │─────────┘
└──────────┘    └──────────┘    └─────────────┘    └────────┘
```

### State Definitions

| Status | Description | Can Transition To | Required Actions |
|--------|-------------|-------------------|------------------|
| `Created` | Task extracted from meeting | `Assigned`, `Blocked` | Auto-generated |
| `Assigned` | Owner assigned | `In-Progress`, `Blocked` | Owner must acknowledge |
| `In-Progress` | Active work happening | `Review`, `Blocked` | Owner working |
| `Review` | Work complete, pending verification | `Verified`, `Failed`, `In-Progress` | Perplexity reviews |
| `Verified` | All criteria confirmed met | `Complete` | Verification proof recorded |
| `Complete` | Task fully done | (terminal) | Moved to `tasks/completed/` |
| `Blocked` | Cannot proceed | Previous state | Blocker documented |
| `Failed` | Verification failed | `In-Progress` | Failure reason documented |

---

## Mandatory Verification Step

### The "No Phantom Tasks" Rule

**A task CANNOT be marked `Complete` without going through `Verified` status.**

### Verification Process

1. **Owner marks task as `Review`**
   - All work must be committed/deployed
   - Owner documents what was done

2. **Perplexity performs verification**
   - Checks each verification criterion
   - Documents evidence for each
   - Records pass/fail for each criterion

3. **Verification outcome**
   - **All pass:** Status → `Verified` → `Complete`
   - **Any fail:** Status → `Failed` (returns to `In-Progress`)

### Verification Record

```yaml
verification_record:
  verifier: perplexity
  verified_at: 2026-02-21T18:45:00Z
  criteria_results:
    - criterion: "Code passes all unit tests"
      result: pass
      evidence: "CI run #4521 - all 47 tests passed"
    - criterion: "Documentation updated"
      result: pass  
      evidence: "docs/api.md updated in commit a1b2c3d"
    - criterion: "PR merged to main branch"
      result: pass
      evidence: "PR #123 merged at 2026-02-21T17:30:00Z"
  overall_result: verified
```

---

## File Locations

| Status | Location | Naming |
|--------|----------|--------|
| `Created` | `tasks/backlog/` | `{task-id}.md` |
| `Assigned` | `tasks/active/` | `{task-id}.md` |
| `In-Progress` | `tasks/active/` | `{task-id}.md` |
| `Review` | `tasks/review/` | `{task-id}.md` |
| `Verified` | `tasks/review/` | `{task-id}.md` |
| `Complete` | `tasks/completed/` | `{task-id}.md` |
| `Blocked` | `tasks/blocked/` | `{task-id}.md` |

---

## BPR&D-To-Do-List Integration

### Sync Rules

1. The master `BPR&D-To-Do-List.md` is auto-generated from task files
2. Manual edits to the list are prohibited
3. Changes must be made to individual task files
4. Sync runs on every commit via pre-commit hook

### List Format

See [`_shared/templates/todo-list-v2.md`](../../_shared/templates/todo-list-v2.md) for the v2 format.

---

## Automation Enforcement

### Pre-commit Checks

1. All tasks have valid IDs matching `BPRD-{YYYY}-{NNNN}`
2. Required fields are present
3. Status transitions are valid
4. `Complete` status only allowed with verification record
5. Owner must be in agent registry

### CI Validation

1. No duplicate task IDs
2. All source links are valid
3. Skill-web nodes exist
4. No orphaned task files

---

## Examples

### Creating a New Task

```bash
# Automatically generated from meeting transcript
# See: meeting-code-deployer.md
```

### Task File Example

```markdown
---
id: BPRD-2026-0042
source: meetings/transcripts/meeting-2026-02-21-14-30-sprint-planning.md#L45
skill_web_node: skills/code-review
owner: claude
status: In-Progress
created_at: 2026-02-21T14:35:00Z
updated_at: 2026-02-21T16:20:00Z
priority: high
due_date: 2026-02-25
verification_criteria:
  - "Code passes all unit tests"
  - "Documentation updated"
  - "PR merged to main branch"
---

# Implement API Rate Limiting

## Context
Extracted from sprint planning meeting. Discussion at line 45-52 of transcript.

## Requirements
- Add rate limiting middleware to FastAPI endpoints
- Configure per-user and global limits
- Add monitoring dashboard

## Progress
- [x] Research rate limiting options
- [ ] Implement middleware
- [ ] Add configuration
- [ ] Write tests

## Notes
Consider using slowapi library for FastAPI compatibility.
```
