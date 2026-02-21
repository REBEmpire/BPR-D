# BPR&D To-Do List v2

**Last Updated:** {{last_updated}}  
**Auto-generated:** Yes (do not edit manually)  
**Source:** Individual task files in `tasks/` directory

---

## Quick Stats

| Status | Count |
|--------|-------|
| 🔴 Created | {{count_created}} |
| 🟡 Assigned | {{count_assigned}} |
| 🔵 In-Progress | {{count_in_progress}} |
| 🟣 Review | {{count_review}} |
| 🟢 Verified | {{count_verified}} |
| ⬜ Blocked | {{count_blocked}} |

---

## Active Tasks

### 🔴 Created (Unassigned)

| ID | Task | Skill | Source | Priority | Created |
|----|------|-------|--------|----------|--------|
{{#each tasks_created}}
| [{{id}}](tasks/backlog/{{id}}.md) | {{title}} | [{{skill_name}}]({{skill_link}}) | [Meeting]({{source}}) | {{priority}} | {{created_at}} |
{{/each}}

### 🟡 Assigned

| ID | Task | Owner | Skill | Source | Due |
|----|------|-------|-------|--------|-----|
{{#each tasks_assigned}}
| [{{id}}](tasks/active/{{id}}.md) | {{title}} | {{owner}} | [{{skill_name}}]({{skill_link}}) | [Meeting]({{source}}) | {{due_date}} |
{{/each}}

### 🔵 In-Progress

| ID | Task | Owner | Skill | Progress | Started |
|----|------|-------|-------|----------|--------|
{{#each tasks_in_progress}}
| [{{id}}](tasks/active/{{id}}.md) | {{title}} | {{owner}} | [{{skill_name}}]({{skill_link}}) | {{progress_pct}}% | {{started_at}} |
{{/each}}

### 🟣 Review (Pending Verification)

| ID | Task | Owner | Verifier | Submitted | Criteria Met |
|----|------|-------|----------|-----------|-------------|
{{#each tasks_review}}
| [{{id}}](tasks/review/{{id}}.md) | {{title}} | {{owner}} | {{verifier}} | {{submitted_at}} | {{criteria_met}}/{{criteria_total}} |
{{/each}}

### ⬜ Blocked

| ID | Task | Owner | Blocker | Blocked Since |
|----|------|-------|---------|---------------|
{{#each tasks_blocked}}
| [{{id}}](tasks/blocked/{{id}}.md) | {{title}} | {{owner}} | {{blocker_description}} | {{blocked_at}} |
{{/each}}

---

## Recently Completed

| ID | Task | Owner | Verified By | Completed |
|----|------|-------|-------------|----------|
{{#each tasks_completed_recent}}
| [{{id}}](tasks/completed/{{id}}.md) | {{title}} | {{owner}} | {{verified_by}} | {{completed_at}} |
{{/each}}

[View All Completed Tasks](tasks/completed/)

---

## By Owner

{{#each owners}}
### {{name}} ({{count}} tasks)

| ID | Task | Status | Priority |
|----|------|--------|----------|
{{#each tasks}}
| [{{id}}]({{path}}) | {{title}} | {{status}} | {{priority}} |
{{/each}}

{{/each}}

---

## By Skill

{{#each skills}}
### [{{name}}]({{skill_link}}) ({{count}} tasks)

| ID | Task | Owner | Status |
|----|------|-------|--------|
{{#each tasks}}
| [{{id}}]({{path}}) | {{title}} | {{owner}} | {{status}} |
{{/each}}

{{/each}}

---

## Meeting Sources

| Meeting | Date | Tasks Generated | Completed |
|---------|------|-----------------|----------|
{{#each meetings}}
| [{{topic}}]({{link}}) | {{date}} | {{tasks_count}} | {{completed_count}} |
{{/each}}

---

## Verification Queue

Tasks awaiting verification by Perplexity:

| ID | Task | Owner | Waiting Since | Criteria |
|----|------|-------|--------------|----------|
{{#each verification_queue}}
| [{{id}}](tasks/review/{{id}}.md) | {{title}} | {{owner}} | {{waiting_since}} | {{criteria_count}} items |
{{/each}}

---

## How This List Works

1. **Auto-generated**: This file is regenerated on every commit
2. **Do not edit**: Changes will be overwritten
3. **To add tasks**: Create meeting transcript or use MCD pipeline
4. **To update**: Edit individual task files in `tasks/`
5. **Task IDs**: Format `BPRD-YYYY-NNNN`

### Status Flow

```
Created → Assigned → In-Progress → Review → Verified → Complete
    ↓         ↓            ↓           ↓
 Blocked   Blocked     Blocked      Failed
```

### Links

- [Work Item Protocol](docs/v2-architecture/work-item-protocol.md)
- [Meeting-Code-Deployer](docs/v2-architecture/meeting-code-deployer.md)
- [Skill-Web](docs/v2-architecture/skill-web-integration.md)

---

*Generated at {{generated_at}} by v2 automation*
