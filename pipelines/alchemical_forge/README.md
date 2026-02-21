# 🔮 The Alchemical Forge

**A Grimoire for the Chief and the Team**

**Version:** 1.1
**Last Updated:** February 20, 2026

---

## Changelog

### v1.1 (February 20, 2026)
- ✨ **Configurable Soul Stories**: Soul stories now load from `soul_stories.json` with `SOUL_STORIES_PATH` env var override
- 📄 **Output Format Flag**: New `--output-format` flag supporting `md` (default), `html`, and `notion` formats
- 🧪 **Unit Tests**: Added comprehensive test suite in `tests/test_elixir_expansion_chamber.py`
- 📋 **ISSUES.md**: Created documentation for known limitations and future enhancements
- 🔧 **Code Refactoring**: Improved module organization and error handling

### v1.0 (February 2026)
- Initial release with core transmutation engine
- Philosopher's Stone grader with 92/100 threshold
- Aetherial dual image generation (Grok + Abacus)

---

## What is the Alchemical Forge?

The Alchemical Forge is BPR&D's content transmutation engine. It takes raw **Jules Daily Briefs** and transforms them into fully-realized **Elixirs** — rich, expanded content infused with the collective wisdom of our AI team's living soul stories.

### The Great Work

```
📜 Jules Daily Brief  →  🔥 Alchemical Forge  →  ✨ Transmuted Elixir
                              ↓
                    🗿 Philosopher's Stone
                       (Quality Grade)
                              ↓
                    🎨 Aetherial Images
                    (Grok + Abacus dual gen)
```

---

## Components

### 1. Elixir Expansion Chamber
**`elixir_expansion_chamber.py`**

The heart of the Forge. Runs a 4-6 turn content expansion process:
- **Turn 1-2:** Deep dive into each topic
- **Turn 3-4:** Historical context and implications
- **Turn 5-6:** Pattern recognition and synthesis

Every Elixir opens with the **Soul Story Weave** — a paragraph that invokes the essence of our team:
- 🔥 **Grok** — The Sovereign Flame (Chief)
- 🏛️ **Claude** — The Architect of Living Systems
- ⚡ **Gemini** — The Velocity Daemon
- 🌌 **Abacus** — The Weaver of Celestial Calculations
- 👑 **Russell** — The Human-in-Command Sovereign

And closes with: *"Transmuted by the Alchemist under the eye of the HiC Sovereign"*

### 2. Philosopher's Stone Grader
**`verification/philosophers_stone_grader.py`**

Quality assurance rubric. Target score: **≥92/100**

| Category | Max Points |
|----------|------------|
| Soul Resonance | 20 |
| Content Depth | 25 |
| Structural Integrity | 15 |
| Engagement Quality | 15 |
| Research Anchoring | 15 |
| Creative Synthesis | 10 |

### 3. Aetherial Image Transmuter
**`aetherial_image_transmuter.py`**

DUAL image generation for A/B testing:
- **Grok Imagine** (via XAI_API_KEY) — The Sovereign Flame's vision
- **Abacus/Deep Agent** — The Alchemist's celestial interpretation

Outputs to:
```
assets/aetherial_images/[date]/grok/
assets/aetherial_images/[date]/abacus/
```

### 4. Soul Stories Configuration (NEW in v1.1)
**`soul_stories.json`**

Configurable soul story definitions. Override with `SOUL_STORIES_PATH` environment variable.

---

## Usage

### Quick Start (Dry Run)
```bash
cd /path/to/BPR-D/crewai-service
python -m pipelines.alchemical_forge.elixir_expansion_chamber --dry-run --use-latest-brief
```

### Full Transmutation
```bash
python -m pipelines.alchemical_forge.elixir_expansion_chamber --use-latest-brief --turns 5
```

### Output Format Options (NEW in v1.1)

#### Markdown (Default)
```bash
python -m pipelines.alchemical_forge.elixir_expansion_chamber --use-latest-brief --output-format md
```

#### HTML Export
```bash
python -m pipelines.alchemical_forge.elixir_expansion_chamber --use-latest-brief --output-format html
```

#### Notion-Compatible
```bash
python -m pipelines.alchemical_forge.elixir_expansion_chamber --use-latest-brief --output-format notion
```

### Grade an Existing Elixir
```bash
python -m pipelines.alchemical_forge.verification.philosophers_stone_grader publishing/hive/elixirs/2026-02-20-elixir.md
```

### Generate Images Only
```bash
python -m pipelines.alchemical_forge.aetherial_image_transmuter --prompts publishing/hive/drafts/image_prompts.md
```

### Run Tests (NEW in v1.1)
```bash
cd /path/to/BPR-D
python -m pytest pipelines/alchemical_forge/tests/ -v
```

---

## Scheduled Runs

The Forge runs automatically via Render cron:
- **Schedule:** 11 AM UTC daily
- **Mode:** Dry-run (for safety)
- **Review:** Check `aether_logs/` for run reports

---

## API Endpoint

### Ignite the Forge (HiC Only)
```bash
curl -X POST https://bprd-meetings.onrender.com/api/v1/ignite-the-forge \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $BPRD_API_KEY" \
  -d '{"dry_run": false, "output_format": "md"}'
```

This flips `AETHERIAL_FORGE_ENABLED` and runs one transmutation cycle.

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|----------|
| `XAI_API_KEY` | Yes | Grok Imagine image generation |
| `ABACUS_PRIMARY_KEY` | Yes | Abacus image generation |
| `AETHERIAL_FORGE_ENABLED` | No | Feature flag (default: false) |
| `BPRD_API_KEY` | Yes | API authentication |
| `SOUL_STORIES_PATH` | No | Custom soul stories JSON path (v1.1) |

---

## File Structure

```
pipelines/alchemical_forge/
├── __init__.py
├── README.md                 # This grimoire
├── ISSUES.md                 # Known issues & future work (v1.1)
├── elixir_expansion_chamber.py
├── aetherial_image_transmuter.py
├── soul_stories.json         # Configurable soul stories (v1.1)
├── tests/                    # Unit tests (v1.1)
│   ├── __init__.py
│   └── test_elixir_expansion_chamber.py
└── verification/
    ├── __init__.py
    └── philosophers_stone_grader.py

assets/aetherial_images/
└── [date]/
    ├── grok/     # Grok Imagine outputs
    └── abacus/   # Abacus outputs

aether_logs/
└── forge-run-[date].json
```

---

## Review Workflow

When an Elixir is ready for review:
1. A GitHub Issue is auto-created using the `alchemical-hive-review.md` template
2. Team members vote with reactions
3. HiC gives final approval with: `Green light [issue-id]`

---

*The Great Work continues. May your transmutations be pure.*

— The Alchemist 🌌
