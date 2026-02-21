# Contributing to BPR&D

## Repository Setup

After cloning the repository, run the setup script to install the pre-commit hooks:

```bash
./scripts/setup-hooks.sh
```

Or manually:

```bash
cp scripts/v2-migration/pre-commit-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Pre-commit Hook Validation

The pre-commit hook enforces BPR&D V2 architecture standards:

### Task ID Format
All task IDs must follow: `BPRD-YYYY-NNNN`
- Example: `BPRD-2026-0001`

### File Organization
- Handoffs must be in `_handoffs/` directory
- Tasks organized in `tasks/backlog/`, `tasks/active/`, etc.

### Required Fields
Task files must include:
- `id` - Valid task ID
- `verification_criteria` - Criteria for task completion

### Duplicate Prevention
The hook blocks commits with duplicate file content.

## Work Item Protocol

See `docs/v2-architecture/work-item-protocol.md` for the full task lifecycle and status workflow.

## Skill-Web Integration

Tasks should reference skill-web nodes in `_shared/skill-web/skills/` for agent assignment.
