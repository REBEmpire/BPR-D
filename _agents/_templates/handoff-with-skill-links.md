---
Date: YYYY-MM-DD
Author: "[Agent Name] | Model: [model-id]"
Version: v1.0
Status: open
negation_test: |
  Describe the condition under which this task would FAIL silently.
  Example: "FAIL if: Generated summary omits critical risk factors mentioned in source"
---

# Handoff: [Descriptive Title]

**Status**: open
**Priority**: [URGENT|High|Medium|Low]
**Assigned to**: [Agent or Russell]
**Due date**: YYYY-MM-DD
**Created by**: [Creating Agent]

<!-- SKILL GRAPH LINKS: Add [[wiki-links]] to relevant skill nodes below.
     Backlog discovery will traverse these links (depth 3) to inject
     procedural context into the assigned agent's session prompt.

     Common links to include:
     - [[skill-handoff-protocols]] — always include
     - [[skill-cost-governance]] — if budget decisions involved
     - [[skill-hive-content-pipeline]] — if Hive publishing involved
     - [[skill-quality-filter]] — if content review involved
     - [[skill-github-commit-automation]] — if commits/PRs involved
     - [[skill-render-deployment]] — if deployment involved
     - [[skill-research-brief-format]] — if research output involved
-->

**Related Skills**: [[skill-handoff-protocols]] | [[ADD MORE]]

---

## Context
[Why this task exists, what triggered it, relevant background.
Include specific file paths, error messages, or decision context.]

## Acceptance Criteria
- [ ] [Specific measurable outcome 1]
- [ ] [Specific measurable outcome 2]
- [ ] [Specific measurable outcome 3]

## Dependencies
- [What must be done or available before this can proceed]
- [Other handoffs this depends on, if any]

## Approach (Optional)
[Suggested implementation approach if you have one]

## Notes
[Additional context, risks, or considerations]

---
<!-- Archive this file to _agents/_handoffs/archive/ when complete -->
