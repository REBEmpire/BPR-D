# Knowledge System & Skill Webs v2.0

## Architecture

The v2.0 system replaces the file-based v1 with a dual-layer graph architecture for scalable knowledge and skill management.

### Knowledge Graph
- **Backend**: NetworkX undirected graph + SQLite persistence (nodes/edges tables).
- **Nodes**: Entities/facts/concepts with type, props (text, source, timestamp), embeddings (SentenceTransformers).
- **Edges**: Relations (knows, part_of, causes) with props (confidence, source).
- **Persistence**: Atomic SQLite txns; JSONL snapshots for versioning.
- **Neo4j Compat**: `export_cypher()` generates Cypher queries for import.

### Skill Web
- **Backend**: NetworkX directed acyclic graph (DAG) + SQLite persistence (skills/prereqs tables).
- **Nodes**: Skills with mastery (0-100), confidence (0-1), updated timestamp, citations list, props.
- **Edges**: Prerequisites (prereq → skill).
- **Validation**: Topological sort ensures no cycles.
- **Persistence**: SQLite with atomic saves.

### Auto-Discovery
- **LLM Extraction**: Structured prompts via LiteLLM (GPT-4o-mini fallback) extract triples/skills from text.
- **Integration**: `ingest_from_interaction(text, source)` auto-adds to graphs.
- **Sources**: Conversations, commits, tool outputs.

### Query Layer
- **NL Search**: Embed query → cosine similarity top-k nodes (FAISS-like).
- **Skill Paths**: `nx.shortest_path()` for routes; PageRank for "learn next".
- **Learning Paths**: Topo-sort prereqs with mastery gaps/effort estimates.

### Exports
- **Markdown**: Human-readable graph dumps.
- **JSON**: Structured data for tools.
- **Cypher**: Neo4j import.

## Usage Examples

### Basic Usage
```python
from knowledge_system.knowledge_graph_v2 import KnowledgeGraph
from skill_webs.skill_web_v2 import SkillWeb

kg = KnowledgeGraph()
sw = SkillWeb()

# Add knowledge
kg.add_fact('Python', 'is_a', 'Programming Language', {'source': 'manual'})

# Add skill
sw.add_skill('Python Basics', prereqs=['Programming Concepts'], mastery=50, confidence=0.8)

# Query
results = kg.query_nl('programming languages', top_k=3)
path = sw.generate_learning_path('Advanced Python', {'Python Basics': 30})
```

### Auto-Ingest
```python
conversation = "Grok learned that NetworkX is great for graphs."
kg.ingest_from_interaction(conversation, 'chat')
```

### Migration
```bash
python knowledge_system/upgrade_migration.py --dry-run
python knowledge_system/upgrade_migration.py  # Run migration
```

## API Reference

### KnowledgeGraph
- `__init__(db_path='knowledge.db', embed_model='all-MiniLM-L6-v2')`
- `add_fact(subj, pred, obj, props={})`: Add/update triple.
- `query_nl(query, top_k=5)`: List[Dict] with similarity scores.
- `export_cypher()`: List[str] Cypher queries.
- `export_to_jsonl(version)`: Save snapshot.
- `ingest_from_interaction(text, source)`: Auto-extract + add.

### SkillWeb
- `__init__(db_path='skill_web.db', embed_model='all-MiniLM-L6-v2')`
- `add_skill(skill_id, prereqs=[], mastery=0, confidence=0.5, citations=[], props={})`: Add/update skill.
- `upgrade_skill_web(current_web, new_evidence)`: LLM merge evidence.
- `generate_learning_path(target_skill, current_mastery)`: List[Dict] with gaps/effort.
- `export_to_markdown()`: str.
- `export_to_json()`: Dict.

### Utils
- `extract_knowledge(text, source)`: List[Dict] triples.
- `extract_skills(text, source)`: List[Dict] skills.

## Migration Guide
1. Backup v1 dirs.
2. Install deps: `pip install -r requirements.txt`
3. Run dry-run to validate.
4. Execute migration; snapshots saved.
5. Verify graphs: `kg.G.nodes()`, `sw.G.edges()`.

## Dependencies
- networkx, sqlite3, openai, sentence-transformers, litellm, pytest, numpy.

## Future Extensions
- Vector DB for large-scale search.
- Graph RAG for context retrieval.
- UI for visualization.