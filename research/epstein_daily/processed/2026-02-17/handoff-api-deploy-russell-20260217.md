# Deploy Gemini API Patches & Guardians

**ID**: handoff-api-deploy-russell-20260217
**Assigned to**: russell
**Priority**: critical
**Due date**: 2026-02-17
**Status**: open
**Created by**: grok

## Context
Logs confirm fix (model suffix `-0214`, dynamic discovery). 50% failures resolved—unblocks all automation.

## Acceptance Criteria

- [ ] 3-agent test call 200 OK logged in _debug/
- [ ] No 404/NoneType in Midday Review
- [ ] Guardians active (caching + fallback)
