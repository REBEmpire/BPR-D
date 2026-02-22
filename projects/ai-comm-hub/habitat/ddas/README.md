# DDAS MVP - Functional Specification

**Project:** DDAS (Decentralized Digital Arts Studio) Habitat
**Status:** MVP Prototype
**Assigned Agent:** Claude

## Overview
The DDAS MVP aims to demonstrate a basic pipeline for ingesting research briefs, processing them through a knowledge graph to identify contradictions, and generating actionable insights. This module serves as the core logic for the "Habitat" environment where agents collaborate.

## Core Components

1.  **Ingestion Engine:**
    -   Input: Markdown briefs (e.g., Daily Briefs, Raw Digests).
    -   Process: Extracts entities and claims.

2.  **Contradiction Engine:**
    -   Logic: Compare new claims against existing knowledge (mocked for MVP).
    -   Output: Report highlighting conflicts or novel insights.

3.  **Prototype Script (`ddas_prototype.py`):**
    -   A standalone Python script demonstrating the flow.
    -   Usage: `python3 ddas_prototype.py`

## MVP Scope
-   **Input:** Hardcoded or simple file reading of a sample brief.
-   **Processing:** Heuristic-based entity extraction (regex/keywords).
-   **Output:** Console output of "Contradiction Report".

## Future Roadmap
-   Integration with Neo4j/NetworkX for persistent graph storage.
-   LLM-based claim extraction (Abacus/Claude).
-   Multi-agent debate resolution interface.
