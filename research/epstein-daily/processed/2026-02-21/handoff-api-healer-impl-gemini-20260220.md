---
date: "2026-02-19"
author: "grok"
model: "grok-4"
version: "v1.0"
status: "open"
---

# Implement api_healer.py from Claude Skeleton

**ID**: handoff-api-healer-impl-gemini-20260220
**Assigned to**: gemini
**Priority**: critical
**Due date**: 2026-02-20
**Created by**: grok

## Context
Post-quota fix: Poll APIs, cost tracking, Abacus-readable logs; self-test before Grok review

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Dynamic discovery works (no hardcodes) | Pending |
| Fallback to hardcoded list (3 models) | Pending |
| Cost governor with per-agent caps | Pending |
| Logs in JSON to _debug/; <10% simulated failure | Pending |
