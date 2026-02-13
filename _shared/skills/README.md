# BPR&D Skills Library

Skills are folders of instructions, scripts, and resources that AI agents load dynamically to improve performance on specialized tasks.

## Directory Structure

```
_shared/skills/
├── coding/           # Development and technical skills
│   ├── frontend-design/
│   ├── mcp-builder/
│   └── webapp-testing/
├── communication/    # Writing and messaging skills
│   ├── brand-guidelines/
│   └── internal-comms/
├── creative/         # Art and design skills
│   └── algorithmic-art/
├── data/            # Data analysis and spreadsheets
│   └── xlsx/
├── document/        # Document creation and editing
│   ├── docx/
│   ├── pdf/
│   └── pptx/
├── meta/            # Skills for creating skills
│   └── skill-creator/
└── trading/         # Trading and finance skills (TBD)
```

## Skill Format

Each skill is a folder containing at minimum a `SKILL.md` file:

```markdown
---
name: skill-name
description: Brief description for discovery - when should this be used?
---

# Skill Name

[Instructions that the AI follows when this skill is active]
```

### Frontmatter Fields
- `name`: Unique identifier (lowercase, hyphens)
- `description`: Concise description for skill discovery (~100 tokens)

### Full Instructions
- Keep under 5k tokens
- Write conversationally, as if addressing a collaborator
- Include specific examples over vague descriptions
- Add constraints for what NOT to do

## How Skills Load

1. **Discovery** (~100 tokens): Frontmatter is read to determine relevance
2. **Full Load** (<5k tokens): Complete instructions loaded when skill is invoked
3. **Resources** (on-demand): Additional files in skill folder loaded as needed

Multiple skills can be registered without overwhelming context - they only consume tokens when actively used.

## Agent Assignments

| Skill | Primary Agents | Use For |
|-------|---------------|---------|
| docx, pdf, pptx | Claude, Gemini | Document creation |
| xlsx | Gemini, Abacus | Data analysis |
| mcp-builder | Gemini, Abacus | MCP servers |
| webapp-testing | Gemini | Browser testing |
| frontend-design | Gemini | React/Tailwind |
| algorithmic-art | Arts Studio project | Generative art |
| brand-guidelines | Gemini, Claude | Branding |
| internal-comms | Claude, Gemini | Reports, newsletters |
| skill-creator | Claude, Grok | Building new skills |

## Creating New Skills

1. Copy template from `_shared/templates/skill.md`
2. Create folder in appropriate category
3. Add `SKILL.md` with frontmatter and instructions
4. (Optional) Add `scripts/`, `reference/`, or `examples/` folders
5. Test with relevant agent before considering it stable

## Sources

These skills are from the official [anthropics/skills](https://github.com/anthropics/skills) repository:
- **Document skills** (docx, pdf, pptx, xlsx): Source-available, production-grade
- **Development skills**: Open source (Apache 2.0)
- **Communication skills**: Open source (Apache 2.0)

See also:
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) - Community collection
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Battle-tested configs
