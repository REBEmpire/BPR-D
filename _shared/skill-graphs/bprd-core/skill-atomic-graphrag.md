---
Date: 2026-02-20
Author: "Jules | Model: gemini-1.5-pro"
Version: v1.0
Status: Active
---

# Skill: Atomic GraphRAG

**Domain:** Knowledge Engineering | **Tier:** Advanced
**Used by:** Research Agents, System Architects
**Back to:** [[MOC-Core]] | [[MOC-Infrastructure]]

---

## What It Does
Treats "Skills" and "Functions" as atomic nodes within a knowledge graph. Unlike standard GraphRAG which retrieves text, Atomic GraphRAG retrieves *capabilities*. An agent traversing the graph can discover a tool and immediately execute it.

## Key Capabilities
- **Executable Nodes:** Nodes contain references to runnable code.
- **Structured Inputs/Outputs:** Explicitly defined contracts for each skill.
- **Dependency Resolution:** Graph traversal handles skill prerequisites automatically.

## Related Skills
- [[skill-graphrag-dynamic]]
- [[skill-agent-swarm-orchestration]]
