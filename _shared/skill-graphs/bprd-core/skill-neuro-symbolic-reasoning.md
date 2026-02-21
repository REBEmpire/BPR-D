---
Date: 2026-02-22
Author: "Jules | Model: gemini-1.5-pro"
Version: v1.0
Status: Active
---

# Skill: Neuro-Symbolic Reasoning

**Domain:** AI Safety | **Tier:** Advanced
**Used by:** Research Agents, Quality Gate
**Back to:** [[MOC-Core]] | [[skill-quality-filter]]

---

## What It Does
Integrates formal logic solvers (like Z3 or Prolog) into the LLM inference chain. This ensures that generated code, math, or logical deductions are mathematically proven to be correct before being presented to the user, eliminating "hallucinations" in critical paths.

## Key Capabilities
- **Formal Verification:** mathematically proves code correctness against a spec.
- **Logic Constraints:** Enforces strict logical rules on LLM output.
- **Self-Correction:** Feeds solver errors back to the LLM for iterative fixing.

## Related Skills
- [[skill-image-prompt-standards]]
- [[skill-atomic-graphrag]]
