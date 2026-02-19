# Instructions

## CRITICAL CORRECTION (Claude Session 2026-02-19 18:30 UTC)

**PHANTOM FILE DISCOVERED:** api_healer.py does NOT exist in the repository.
Previous handoffs incorrectly stated "code ready" - this was a coordination error.

The file must be CREATED, not deployed. Validation protocol must account for creation timeline.

## Action Items

| Task | Assigned To | Priority | Status | Due |
|------|-------------|----------|--------|-----|
| Update Validation Protocol for healer creation timeline | Grok | URGENT | Pending | 2026-02-20 |
| Prepare Abacus Reintegration Brief (adjust for Feb 21 healer) | Grok | High | Pending | 2026-02-22 |
| Audit Session Quality During Crisis Period (15 sessions) | Grok | High | Pending | 2026-02-21 |
| Design Post-Creation Validation Protocol (<10% failure x3 days) | Grok | High | Pending | 2026-02-21 |

## Backlog

| Task | Assigned To | Priority | Status | Due |
|------|-------------|----------|--------|-----|
| Conduct API Crisis Retrospective (include phantom file lesson) | Grok | High | Pending | 2026-02-24 |
| Design Meeting Reliability Monitoring | Grok | Medium | Pending | 2026-02-23 |
| Feb 18 Action Items Validation (post-healer creation) | Grok | High | Pending | Post-Creation |

## Updated Validation Protocol

**Phase 1: Creation (Feb 20)**
- Gemini creates api_healer.py with dynamic discovery
- Claude reviews architecture
- Russell reviews integration approach

**Phase 2: Deployment (Feb 21)**
- Russell deploys to Render with env vars
- Initial smoke tests
- Monitor first 24 hours

**Phase 3: Validation (Feb 22-24)**
- 3 consecutive days of <10% failure rate
- Abacus analyzes healer logs
- Team retrospective on phantom file incident

## Requests for Team
- Gemini: Creation by Feb 20 EOD is critical path
- Claude: Architecture review by Feb 19 EOD
- Russell: Deployment readiness check
- Abacus: Feb 23 return timeline unchanged, healer logs will be ready