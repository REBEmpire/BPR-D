---
Date: 2026-02-19
Author: "Jules | Model: gemini-1.5-pro"
Version: v1.0
Status: Active
---

# Skill: Contextual Memory Mesh

**Domain:** Cognitive Architecture | **Tier:** Core
**Used by:** All Agents
**Back to:** [[MOC-Core]] | [[MOC-Infrastructure]]

---

## What It Does
Provides a shared, persistent memory layer accessible by all agents in the system. Stores conversation history, extracted facts, and user preferences in a vector database + graph structure.

## Key Capabilities
- **Cross-Session Persistence:** Memory survives restarts.
- **Shared Context:** Agent A knows what Agent B learned.
- **Semantic Recall:** Retrieve memories by meaning, not just keywords.

## Related Skills
- [[skill-memory-types]]
- [[skill-agent-self-evolution]]
