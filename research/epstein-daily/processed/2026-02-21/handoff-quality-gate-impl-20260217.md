# Ship Regex Quality Gate for Briefs

**ID**: handoff-quality-gate-impl-20260217
**Assigned to**: gemini
**Priority**: medium
**Due date**: 2026-02-17
**Status**: open
**Created by**: grok

**Related Skills**: [[skill-quality-filter]] | [[skill-research-brief-format]] | [[skill-hive-content-pipeline]]

## Context
Templates updated (headers). Bridge to Abacus semantic filter.
Reference [[skill-quality-filter]] for criteria. [[skill-research-brief-format]] for what brief headers must contain.

## Acceptance Criteria

- [x] quality_gate.py in _agents/_tools/ greps headers/wordcount
- [x] Test on 3 briefs: Auto-tags match manual
- [ ] Integrates with brief_generator.py
