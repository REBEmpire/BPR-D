---
title: MeetingCodeDeployer — Agent Specification
date: 2026-02-20
author: HiC Russell via Chief Grok
status: Draft — Phase 1 MVP
---

# MeetingCodeDeployer

## Purpose

Turn meetings into instant deliverables. Any code block tagged with ` ```ship-to-repo ` during **any meeting** (Fire Team or Daily Briefing) is automatically extracted, committed, and pushed to the repo post-meeting.

All agents (Grok, Claude, Gemini, Abacus) are encouraged to generate feasible code during meetings when appropriate.

---

## Trigger

When the meeting engine finishes a session (any type), scan the full transcript for code blocks tagged:

~~~
```ship-to-repo path=relative/path/to/file.ext
<code here>
```
~~~

The `path=` attribute specifies the target file in the repo. If omitted, the deployer holds the block for manual routing.

---

## Pipeline

1. **Parse** — Scan meeting transcript for all ` ```ship-to-repo ` blocks
2. **Extract** — Pull code content and target path from each block
3. **Validate**
   - Syntax check (language-aware linting where possible)
   - Path is within repo boundaries (no `../` escapes)
   - File size < 50KB per block
   - No secrets/credentials detected (basic pattern scan)
4. **Branch** — Create `meeting-deploy/YYYY-MM-DD-HH` feature branch
5. **Commit** — One commit per code block, message: `meeting-deploy: <filename> from <meeting-type> <date>`
6. **Push** — Push branch to origin
7. **Notify** — Telegram alert with summary: files deployed, branch name, any blocks that failed validation

---

## Safety Guardrails

| Rule | Detail |
|------|--------|
| Dry-run default | First 2 weeks: extract + validate only, no commit. Log what *would* deploy. |
| Path allowlist | Only deploy to: `crewai-service/`, `_agents/`, `_docs/`, `content/`, `web/src/`, `games/` |
| No overwrites | If target file exists, append `-new` suffix and flag for manual merge |
| Size limit | Max 50KB per block, max 5 blocks per meeting |
| Credential scan | Reject blocks containing patterns: `API_KEY=`, `SECRET=`, `password`, `token` (configurable) |
| Rollback | Branch-based — never commits to `main` directly. Easy to delete branch if bad. |

---

## Integration Points

- **Meeting Engine** (`crewai-service/engine/`): Hook into post-meeting output. The engine already saves full transcripts — deployer reads from the same output.
- **GitHub API**: Uses existing `GITHUB_TOKEN` from `crewai-service/config.py` for branch/commit/push operations.
- **Telegram**: Uses existing notification infrastructure for deployment alerts.

---

## Agent Guidelines

All agents should consider generating code during meetings when:
- A concrete solution is discussed and consensus is reached
- A config change, template, or documentation update is agreed upon
- A bug fix has a clear implementation
- A new file/spec needs to be created based on discussion

Tag with ` ```ship-to-repo path=target/file.ext ` to queue for auto-deployment.

---

## Phased Rollout

### Phase 1 — MVP (This Week)
- Transcript scanning + code extraction
- Validation pipeline (path, size, credentials)
- Commit to feature branch
- Telegram notification
- **Dry-run mode active** — log only, no actual commits

### Phase 2 — Production (Week 2+)
- Live commits enabled after dry-run validation
- Auto-PR creation from feature branch → main
- PR description auto-generated from meeting context
- Basic test running before merge suggestion

### Phase 3 — Intelligence (Future)
- Language-aware linting per file extension
- Conflict detection with existing code
- Suggested improvements based on repo conventions
- Multi-block dependency resolution (e.g., new file + import update)

---

## Cost Impact

Minimal — runs post-meeting using existing GitHub token. No LLM calls required for extraction/commit pipeline. Only cost is GitHub API calls (free tier).

---

**Owner:** All agents (Grok leads implementation)
**Location:** `_agents/meeting-code-deployer/`
**Status:** Spec complete. Implementation begins this sprint.
