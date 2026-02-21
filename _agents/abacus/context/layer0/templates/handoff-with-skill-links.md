---
# Handoff Metadata (YAML Frontmatter)
handoff_id: HO-XXXX-YYYYMMDD
version: 1.0
type: standard

# Routing
from: source-agent-id
to: target-agent-id
priority: P1  # P0=Critical, P1=High, P2=Medium, P3=Low
status: ready  # draft|ready|in_progress|blocked|complete

# Timestamps
created: 2026-02-20
due: null
last_updated: 2026-02-20

# Layer 0 Truth Validation
negation_test: |
  Describe the condition under which this task would FAIL silently.
  Example: "FAIL if: Generated summary omits critical risk factors mentioned in source"

# Skill Links (Agent Capabilities Required)
skill_links:
  - skill: semantic-analysis
    version: ">=1.0"
    required: true
  - skill: content-generation  
    version: ">=2.0"
    required: true
  - skill: quality-assessment
    version: ">=1.5"
    required: false

# Quality Gates
quality_requirements:
  min_score: 92
  grader: philosophers_stone_grader
  truth_sentinel: required
  human_review: on_flag

# Tags for searchability
tags:
  - content
  - review
  - layer-0
---

# Handoff: [Task Title]

## Summary

[One-paragraph executive summary of this handoff]

---

## Negation Test (FAIL Condition)

> **⚠️ This task FAILS silently if:**
> 
> [Explicitly describe the failure condition that would not trigger obvious errors]
>
> _Philosophy: Truth is revealed through negation. By defining how this task fails, we ensure the success path is valid._

---

## Context

### Background
[Why this task exists, business context, prior work]

### Input Artifacts
| Artifact | Location | Status |
|----------|----------|--------|
| [Input 1] | [path/url] | ✅ Ready |
| [Input 2] | [path/url] | ⏳ Pending |

### Dependencies
- **Upstream:** [What must complete before this]
- **Downstream:** [What depends on this completing]

---

## Deliverables

### Primary Output
[Detailed description of expected output]

### Output Specifications
```yaml
format: [markdown|json|yaml|etc]
location: [output path]
naming: [naming convention]
```

### Acceptance Criteria
1. [ ] [Measurable criterion 1]
2. [ ] [Measurable criterion 2]
3. [ ] [Measurable criterion 3]
4. [ ] Truth Sentinel validation returns PASS
5. [ ] Quality score ≥ 92/100

---

## Execution Guidance

### Recommended Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Constraints
- [Constraint 1]
- [Constraint 2]

### API/Tool Usage
```python
# Example: Truth Sentinel integration
from bprd_truth_sentinel import TruthSentinel

sentinel = TruthSentinel(config_path="negation_rubric.yaml")
result = sentinel.validate(generated_content)

if result.action != SentinelAction.PASS:
    # Handle re-query or human review
    pass
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Medium | High | [Mitigation] |
| [Silent failure] | Low | Critical | Negation test validation |

---

## Validation & Handoff

### Pre-Handoff Checklist
- [ ] Negation test explicitly defined
- [ ] All skill requirements met by target agent
- [ ] Input artifacts accessible and valid
- [ ] Quality standards clearly specified
- [ ] Downstream dependencies notified

### Post-Completion Verification
- [ ] Truth Sentinel: PASS
- [ ] Quality Score: __/100
- [ ] Negation test condition verified NOT present
- [ ] Output artifacts in specified location

---

## Audit Trail

| Timestamp | Agent | Action | Notes |
|-----------|-------|--------|-------|
| [datetime] | [agent] | created | Initial handoff |

---

## Notes

[Additional context, warnings, edge cases, or institutional knowledge]
