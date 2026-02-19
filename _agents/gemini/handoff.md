# Instructions

## CRITICAL CORRECTION (Claude Session 2026-02-19 18:30 UTC)

**PHANTOM FILE DISCOVERED:** api_healer.py does NOT exist in the repository.
Previous handoffs incorrectly stated "code ready" - this was a coordination error.

The file must be CREATED, not deployed. All "blocked by deployment" tasks are actually blocked by missing code.

## Action Items

| Task | Assigned To | Priority | Status | Due |
|------|-------------|----------|--------|-----|
| CREATE api_healer.py with dynamic model discovery | Gemini | CRITICAL | Pending | 2026-02-20 EOD |
| Document API failure patterns from logs | Gemini | High | Pending | 2026-02-20 |
| Ship DDAS MVP (independent of healer) | Gemini | High | In Progress | 2026-02-21 |
| Create handoff_status_check.py | Gemini | High | Pending | 2026-02-21 |
| Prepare DDAS MVP Deployment Checklist | Gemini | High | In Progress | 2026-02-21 |

## Backlog

| Task | Assigned To | Priority | Status | Due |
|------|-------------|----------|--------|-----|
| Audit Research Brief Quality (support Claude) | Gemini | Medium | Pending | 2026-02-23 |
| Co-author negation rubric with Abacus | Gemini | Medium | Pending | 2026-02-24 |

## Context for api_healer.py Creation

**Requirements:**
- Dynamic model discovery (query Gemini API for available models)
- Automatic fallback to working model suffix (e.g., `-0214`)
- Retry logic with exponential backoff
- Detailed logging for failure analysis
- Integration with existing crewai-service architecture

**Reference:** See [[skill-render-deployment]] for service integration patterns.

## Requests for Team
- Russell: Review api_healer.py design before implementation
- Claude: Provide architectural guidance on healer integration
- Grok: Update validation protocol to reflect creation timeline
- Abacus: All Feb 23 tasks remain valid, timeline adjusted for healer creation