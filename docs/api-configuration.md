# BPR&D API Configuration Status v2.0

**Last Updated:** 2026-02-10

---

## Summary

| Agent | Platform | Model | Status | Action Required |
|-------|----------|-------|--------|-----------------|
| Grok | xAI | grok-3 | **WORKING** | None |
| Claude | Anthropic | claude-opus-4-5 | **WORKING** | None |
| Abacus | Abacus.AI | abacus | **CONFIGURED** | SDK client ready in `_agents/abacus/client.py` |
| Gemini | Google AI | gemini-3.0 | Pending | Model upgrade + billing |

---

## Working APIs

### Grok (xAI)
```
Endpoint: https://api.x.ai/v1/chat/completions
Model: grok-3
Auth: Bearer token
Status: OPERATIONAL
```

### Claude (Anthropic)
```
Endpoint: https://api.anthropic.com/v1/messages
Model: claude-opus-4-5
Auth: x-api-key header
Version: 2023-06-01
Status: OPERATIONAL
```

---

## APIs Needing Configuration

### Abacus (Abacus.AI)

**Merged from:** Deep Agent + ChatLLM

**Primary Key:** `<ABACUS_PRIMARY_KEY>`
**Secondary Key (legacy ChatLLM):** `<ABACUS_BACKUP_KEY>`

**Options:**
1. Install Python SDK: `pip install abacusai`
2. Use SDK for agent conversations
3. Alternative: DeepAgent Cloud at https://deepagent.abacus.ai

### Gemini (Google AI / Jules Coding Platform)

**Target Model:** gemini-3.0 (via Jules coding platform)
**Current Key:** Available in credentials.conf.txt
**Legacy Key (Codebuff/Jules):** `<GEMINI_LEGACY_KEY>` -- may provide coding-specific capabilities

**Actions Needed:**
1. Upgrade to paid tier at https://ai.google.dev/
2. Configure for gemini-3.0 models
3. Research Jules/Codebuff platform integration

---

## Orchestrator Requirements

Once all APIs are configured, the orchestrator needs:
1. API Client Classes for each platform
2. Context Loader for profiles and active.md files
3. Conversation Logger for real-time output
4. History Storage for past conversations
5. Handoff Manager for task delegation

---

## Immediate Actions

1. [x] Install abacusai Python SDK and test Abacus access (Configured in `_agents/abacus/client.py`)
2. [ ] Upgrade Gemini API to paid tier
3. [ ] Research Codebuff key for Gemini coding integration
4. [ ] Build orchestrator with working APIs (Grok, Claude) first
5. [ ] Add Abacus and Gemini as APIs come online

---

## Notes

- Grok and Claude can already collaborate via API
- Team consolidated from 6 to 4 agents in February 2026
- Abacus inherits both Deep Agent and ChatLLM API keys
- Full team automation requires completing Abacus and Gemini API setup

*v2.0 -- Updated February 2026 for 4-agent team*
