import networkx as nx
import sqlite3
import json
import datetime
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import litellm
from typing import List, Dict, Any

class KnowledgeGraph:
    def __init__(self, db_path: str = 'knowledge.db', embed_model: str = 'all-MiniLM-L6-v2'):
        self.db_path = db_path
        self.G = nx.Graph()
        self.db = sqlite3.connect(db_path)
        self.encoder = SentenceTransformer(embed_model)
        self._init_db()
        self.load_from_db()

    def _init_db(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT,
                props TEXT,
                embedding BLOB
            )
        ''')
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                src TEXT,
                tgt TEXT,
                rel TEXT,
                props TEXT,
                PRIMARY KEY (src, tgt, rel)
            )
        ''')
        self.db.commit()

    def load_from_db(self):
        cursor = self.db.execute('SELECT id, type, props, embedding FROM nodes')
        for row in cursor:
            id_, type_, props, emb = row
            props = json.loads(props) if props else {}
            emb = emb if emb else None
            self.G.add_node(id_, type=type_, props=props, embedding=emb)

        cursor = self.db.execute('SELECT src, tgt, rel, props FROM edges')
        for row in cursor:
            src, tgt, rel, props = row
            props = json.loads(props) if props else {}
            self.G.add_edge(src, tgt, rel=rel, props=props)

    def save_to_db(self):
        # Clear and reinsert (simple, for prod use UPSERT)
        self.db.execute('DELETE FROM nodes')
        self.db.execute('DELETE FROM edges')

        for node, data in self.G.nodes(data=True):
            props = json.dumps(data.get('props', {}))
            emb = data.get('embedding')
            self.db.execute('INSERT INTO nodes VALUES (?, ?, ?, ?)', (node, data.get('type', 'entity'), props, emb))

        for src, tgt, data in self.G.edges(data=True):
            props = json.dumps(data.get('props', {}))
            self.db.execute('INSERT INTO edges VALUES (?, ?, ?, ?)', (src, tgt, data.get('rel', 'related'), props))

        self.db.commit()

    def add_fact(self, subj: str, pred: str, obj: str, props: Dict[str, Any] = {}):
        # Add nodes if not exist
        for node in [subj, obj]:
            if not self.G.has_node(node):
                emb = self.encoder.encode(node).tobytes()
                self.G.add_node(node, type='entity', props={'created': datetime.datetime.now().isoformat()}, embedding=emb)

        # Add/update edge
        if self.G.has_edge(subj, obj):
            existing = self.G[subj][obj]
            existing['props'].update(props)
        else:
            self.G.add_edge(subj, obj, rel=pred, props=props)

        self.save_to_db()

    def query_nl(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_emb = self.encoder.encode(query)
        results = []
        for node, data in self.G.nodes(data=True):
            if 'embedding' in data and data['embedding'] is not None:
                emb = data['embedding']
                if isinstance(emb, bytes):
                    emb = np.frombuffer(emb, dtype=np.float32)
                similarity = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
                results.append({'node': node, 'similarity': similarity, 'data': data})

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def export_cypher(self) -> List[str]:
        queries = []
        for node, data in self.G.nodes(data=True):
            props = {k: v for k, v in data.items() if k not in ['embedding']}
            props_str = ', '.join(f"{k}: {json.dumps(v)}" for k, v in props.items())
            queries.append(f"CREATE (n:{data.get('type', 'Entity')} {{id: '{node}', {props_str}}})")

        for src, tgt, data in self.G.edges(data=True):
            queries.append(f"MATCH (a {{id: '{src}'}}), (b {{id: '{tgt}'}}) CREATE (a)-[:{data.get('rel', 'RELATED')}]->(b)")

        return queries

    def export_to_jsonl(self, version: str):
        filename = f'knowledge_snapshot_{version}.jsonl'
        with open(filename, 'w') as f:
            for node, data in self.G.nodes(data=True):
                data_copy = data.copy()
                if 'embedding' in data_copy and data_copy['embedding'] is not None:
                    data_copy['embedding'] = np.frombuffer(data_copy['embedding'], dtype=np.float32).tolist()
                json.dump({'type': 'node', 'id': node, **data_copy}, f)
                f.write('\n')
            for src, tgt, data in self.G.edges(data=True):
                json.dump({'type': 'edge', 'src': src, 'tgt': tgt, **data}, f)
                f.write('\n')

    def ingest_from_interaction(self, text: str, source: str):
        triples = extract_knowledge(text, source)
        for triple in triples:
            props = {'source': source, 'confidence': triple.get('confidence', 0.8), 'timestamp': datetime.datetime.now().isoformat()}
            self.add_fact(triple['subj'], triple['pred'], triple['obj'], props)

def extract_knowledge(text: str, source: str) -> List[Dict[str, Any]]:
    prompt = f"""
Extract knowledge triples from the following text. Each triple should be a subject-predicate-object relationship.
Format as JSON list: [{{"subj": "subject", "pred": "predicate", "obj": "object", "confidence": 0.8}}]

Text: {text}
Source: {source}
"""
    try:
        response = litellm.completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip()
        if content.startswith('```json'):
            content = content[7:-3].strip()
        return json.loads(content)
    except Exception as e:
        print(f"LLM extraction failed: {e}. Returning empty.")
        return []