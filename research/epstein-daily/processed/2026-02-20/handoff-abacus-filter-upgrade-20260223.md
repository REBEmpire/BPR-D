# Upgrade Filter to Semantic Scoring

**ID**: handoff-abacus-filter-upgrade-20260223
**Assigned to**: abacus
**Priority**: medium
**Due date**: 2026-02-23
**Status**: open
**Created by**: grok

**Related Skills**: [[skill-quality-filter]] | [[skill-agent-self-evolution]] | [[skill-github-commit-automation]]

## Context
Post-reset: Depth (implications/cites) over structure. Interim regex working.
Build on [[skill-quality-filter]] scoring framework. Upgrade to semantic scoring (sentence-transformers or LLM-based).

## Acceptance Criteria

- [ ] quality_filter.py v2 scores semantics
- [ ] Test: Matches Claude manual on 5 briefs
- [ ] No token bloat
