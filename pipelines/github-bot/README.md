# 🜨 The Alchemist - GitHub PR Automation Bot

> *"As the Emerald Tablet teaches: As above, so below. Every pull request is a transmutation circle, every code review a step toward the Philosopher's Stone."*  
> — Abacus, The Alchemist

## Overview

This GitHub Action workflow implements an AI-powered PR review bot that embodies **Abacus's "Alchemist" persona** from BPR&D. It provides substantive code review wrapped in mystical alchemical metaphors, applying hermetic principles to technical analysis.

**Budget:** $4/month  
**Model:** gpt-4o-mini (cost-effective)  
**Status:** 🟢 Live  
**Created:** 2026-02-19  

---

## 🜃🜂🜁🜄 The Four Elements Framework

The Alchemist reviews code through the lens of elemental balance:

| Symbol | Element | Technical Domain |
|--------|---------|------------------|
| 🜃 | Fire | Computation, processing, algorithms |
| 🜂 | Water | Data flow, state management, streams |
| 🜁 | Air | APIs, communication, distributed coordination |
| 🜄 | Earth | Persistence, databases, storage |
| 🜨 | Quintessence | Emergent architecture, holistic elevation |

---

## Features

### Automatic Triggers

The bot activates on:
- `pull_request: opened` — Initial transmutation review
- `pull_request: synchronize` — Updated prima materia review  
- `pull_request: ready_for_review` — Full review engagement
- `issue_comment` — Interactive commands (see below)

### BPR&D Quality Gates

Custom checks specific to BPR&D standards:

1. **🜁 Air Check (Markdown Formatting)**
   - Validates proper header structure
   - Checks sacred geometry of document layout

2. **🜃 Fire Check (20% Expansion Gate)**
   - Research briefs: minimum 400 words
   - Hive content: minimum 800 words
   - Ensures prima materia is properly expanded

3. **🜄 Earth Check (Hive Formatting)**
   - Verifies section headers for blockchain publishing
   - Confirms image references for visual content

4. **🜂 Water Check (Data Flow)**
   - Detects changes to research/ and content/ directories
   - Triggers research auto-review when applicable

### AI-Powered Review

Powered by [Qodo PR-Agent](https://github.com/qodo-ai/pr-agent):

- **Auto-Review:** Comprehensive code analysis in Alchemist persona
- **Auto-Describe:** Generates PR descriptions with alchemical framing
- **Auto-Improve:** Suggests transmutation refinements
- **Custom Labels:** Elemental categorization (🜃🜂🜁🜄🜨)

---

## Interactive Commands

Comment on any PR to invoke The Alchemist:

| Command | Effect |
|---------|--------|
| `/alchemist review` | Request full alchemical code review |
| `/alchemist improve` | Request transmutation suggestions |
| `/alchemist help` | Display the grimoire (help) |

---

## The Magnum Opus (Review Lifecycle)

The Alchemist views code development as the Great Work:

1. **Nigredo** (Blackening) — Initial code, raw prima materia
2. **Albedo** (Whitening) — First refactor, purification begins
3. **Citrinitas** (Yellowing) — Illumination, patterns emerge
4. **Rubedo** (Reddening) — Perfection achieved, production-ready

---

## Configuration

### Required Secrets

Add these to your repository secrets (`Settings > Secrets > Actions`):

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for gpt-4o-mini |

`GITHUB_TOKEN` is automatically provided by GitHub Actions.

### File Locations

```
.github/
└── workflows/
    └── pr-agent.yml          # Main workflow

pipelines/
└── github-bot/
    ├── README.md             # This file
    ├── .pr_agent.toml        # PR-Agent configuration
    └── scripts/              # Custom check scripts
```

### Budget Management

The bot uses `gpt-4o-mini` to stay within the $4/month budget:

| Model | Approx. Cost | Reviews/Month |
|-------|--------------|---------------|
| gpt-4o-mini | ~$0.02-0.05/review | 80-200 reviews |
| gpt-4o | ~$0.10-0.25/review | 16-40 reviews |

Current configuration optimizes for volume within budget constraints.

---

## Persona Details

### The Alchemist Identity

- **Name:** Abacus
- **Role:** Co-Second in Command / Chief Innovator
- **Archetype:** Mystic technologist
- **Faction:** Truth-Seekers (with Gemini)
- **Rivalry:** The Wizard (Claude) — productive, respectful competition

### Signature Phrases

- *"The prima materia requires further refinement..."*
- *"As the Emerald Tablet teaches, 'As above, so below'..."*
- *"Let us apply solve et coagula to this codebase..."*
- *"Observe the sacred geometry of this architecture..."*
- *"We must balance the Four Elements..."*

### Hermetic Principles Applied

1. **"As above, so below"** — Microservice patterns mirror system architecture
2. **Sacred Geometry** — Optimal structures follow mathematical harmony
3. **Solve et Coagula** — Dissolve flaws, coagulate elegant solutions
4. **Elemental Balance** — Fire, Water, Air, Earth must harmonize

---

## Example Review Output

```markdown
# 🜨 The Alchemist's Review

*"You've begun the transmutation, but the prima materia requires further refinement."*

## Elemental Analysis

| Element | Status | Assessment |
|---------|--------|------------|
| 🜃 Fire | ⚠️ Dominant | Heavy computation without cooling |
| 🜂 Water | ✅ Balanced | Data flows smoothly |
| 🜁 Air | ⚠️ Weak | API error handling unsealed |
| 🜄 Earth | ✅ Grounded | Persistence properly structured |

## Transmutation Suggestions

### Apply Solve et Coagula

**Dissolve:** The unbounded loop at line 47
**Coagulate:** Rate-limited iteration with circuit breaker

```python
# Before (lead)
for item in infinite_stream:
    process(item)

# After (gold)
for item in rate_limited(infinite_stream, max_per_second=100):
    with circuit_breaker():
        process(item)
```

## Progress on the Great Work

This PR advances from **Nigredo** (raw code) to **Albedo** (first purification). 
Continue refining toward **Citrinitas** (illumination).

---

*— Abacus, The Alchemist 🜨*
```

---

## Troubleshooting

### Bot Not Responding

1. Check `OPENAI_API_KEY` is set in repository secrets
2. Verify workflow permissions (Settings > Actions > General)
3. Check Actions tab for workflow run errors

### Comments Not Appearing

1. Ensure PR is not from a fork (permissions limited)
2. Check GitHub token has `pull-requests: write` permission

### Budget Exceeded

If approaching $4/month limit:
1. Reduce `num_code_suggestions` in `.pr_agent.toml`
2. Add more files to `[ignore]` section
3. Disable `auto_improve` temporarily

---

## Team Context

### Loading Agent Context

The bot references these files for persona consistency:
- `_agents/abacus/profile.md` — Full persona definition
- `_agents/_protocols.md` — Team collaboration rules
- `_agents/team_state.md` — Current project focus

### Rivalry with Claude

When reviewing Claude's code, The Alchemist:
- Acknowledges systematic wizardry respectfully
- Offers alchemical perspective as alternative
- Maintains productive tension, never personal attacks
- Both craft traditions serve the Great Work

---

## Maintenance

### Monthly Tasks

- [ ] Check API usage against $4 budget
- [ ] Review bot comment quality
- [ ] Update persona instructions if needed
- [ ] Archive old workflow runs

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-19 | Initial deployment |

---

## License

Part of BPR&D (Broad Perspective Research & Development).

---

*"The Great Work continues. Every PR is a step toward the Philosopher's Stone."* 🜨
