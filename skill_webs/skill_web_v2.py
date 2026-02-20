import networkx as nx
import sqlite3
import json
import datetime
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import litellm
from typing import List, Dict, Any, Tuple

class SkillWeb:
    def __init__(self, db_path: str = 'skill_web.db', embed_model: str = 'all-MiniLM-L6-v2'):
        self.db_path = db_path
        self.G = nx.DiGraph()
        self.db = sqlite3.connect(db_path)
        self.encoder = SentenceTransformer(embed_model)
        self._init_db()
        self.load_from_db()

    def _init_db(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                mastery REAL,
                confidence REAL,
                updated TEXT,
                citations TEXT,
                props TEXT,
                embedding BLOB
            )
        ''')
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS prereqs (
                skill TEXT,
                prereq TEXT,
                PRIMARY KEY (skill, prereq)
            )
        ''')
        self.db.commit()

    def load_from_db(self):
        cursor = self.db.execute('SELECT id, mastery, confidence, updated, citations, props, embedding FROM skills')
        for row in cursor:
            id_, mastery, confidence, updated, citations, props, emb = row
            citations = json.loads(citations) if citations else []
            props = json.loads(props) if props else {}
            emb = emb if emb else None
            self.G.add_node(id_, mastery=mastery, confidence=confidence, updated=updated, citations=citations, props=props, embedding=emb)

        cursor = self.db.execute('SELECT skill, prereq FROM prereqs')
        for row in cursor:
            skill, prereq = row
            self.G.add_edge(prereq, skill)  # prereq -> skill

    def save_to_db(self):
        self.db.execute('DELETE FROM skills')
        self.db.execute('DELETE FROM prereqs')

        for node, data in self.G.nodes(data=True):
            citations = json.dumps(data.get('citations', []))
            props = json.dumps(data.get('props', {}))
            emb = data.get('embedding')
            self.db.execute('INSERT INTO skills VALUES (?, ?, ?, ?, ?, ?, ?)',
                            (node, data.get('mastery', 0), data.get('confidence', 0.5),
                             data.get('updated', datetime.datetime.now().isoformat()),
                             citations, props, emb))

        for src, tgt in self.G.edges():
            self.db.execute('INSERT INTO prereqs VALUES (?, ?)', (tgt, src))  # skill, prereq

        self.db.commit()

    def add_skill(self, skill_id: str, prereqs: List[str] = [], mastery: int = 0, confidence: float = 0.5, citations: List[str] = [], props: Dict[str, Any] = {}):
        if not self.G.has_node(skill_id):
            emb = self.encoder.encode(skill_id).tobytes()
            self.G.add_node(skill_id, mastery=mastery, confidence=confidence,
                            updated=datetime.datetime.now().isoformat(), citations=citations, props=props, embedding=emb)
        else:
            # Update
            data = self.G.nodes[skill_id]
            data['mastery'] = mastery
            data['confidence'] = confidence
            data['updated'] = datetime.datetime.now().isoformat()
            data['citations'].extend(citations)
            data['props'].update(props)

        for prereq in prereqs:
            if not self.G.has_node(prereq):
                emb = self.encoder.encode(prereq).tobytes()
                self.G.add_node(prereq, mastery=100, confidence=1.0, updated=datetime.datetime.now().isoformat(), citations=[], props={}, embedding=emb)
            self.G.add_edge(prereq, skill_id)

        # Validate DAG
        if not nx.is_directed_acyclic_graph(self.G):
            raise ValueError(f"Adding {skill_id} creates cycle")

        self.save_to_db()

    def upgrade_skill_web(self, current_web: 'SkillWeb', new_evidence: str):
        # LLM to resolve updates
        skills_data = extract_skills(new_evidence, 'evidence')
        for skill in skills_data:
            skill_id = skill['id']
            mastery = skill.get('mastery', 0)
            confidence = skill.get('confidence', 0.5)
            citations = skill.get('citations', [])
            prereqs = skill.get('prereqs', [])

            if current_web.G.has_node(skill_id):
                existing = current_web.G.nodes[skill_id]
                # Merge: average mastery/confidence, append citations
                new_mastery = (existing['mastery'] + mastery) / 2
                new_conf = min(1.0, (existing['confidence'] + confidence) / 2)
                existing['citations'].extend(citations)
                existing['updated'] = datetime.datetime.now().isoformat()
                existing['mastery'] = new_mastery
                existing['confidence'] = new_conf
            else:
                current_web.add_skill(skill_id, prereqs, mastery, confidence, citations)

        current_web.save_to_db()

    def generate_learning_path(self, target_skill: str, current_mastery: Dict[str, int]) -> List[Dict[str, Any]]:
        if not self.G.has_node(target_skill):
            return []

        # Find all prereqs
        prereqs = nx.ancestors(self.G, target_skill)
        prereqs.add(target_skill)

        path = []
        for skill in nx.topological_sort(self.G.subgraph(prereqs)):
            mastery = current_mastery.get(skill, 0)
            required = self.G.nodes[skill]['mastery']
            gap = max(0, required - mastery)
            effort = gap * 10  # est tokens or hours
            path.append({
                'skill': skill,
                'current_mastery': mastery,
                'required_mastery': required,
                'gap': gap,
                'estimated_effort': effort,
                'prereqs': list(self.G.predecessors(skill))
            })

        return path

    def export_to_markdown(self) -> str:
        md = "# Skill Web\n\n"
        for skill in nx.topological_sort(self.G):
            data = self.G.nodes[skill]
            md += f"## {skill}\n"
            md += f"- Mastery: {data['mastery']}\n"
            md += f"- Confidence: {data['confidence']}\n"
            md += f"- Citations: {', '.join(data['citations'])}\n"
            prereqs = list(self.G.predecessors(skill))
            if prereqs:
                md += f"- Prerequisites: {', '.join(prereqs)}\n"
            md += "\n"
        return md

    def export_to_json(self) -> Dict[str, Any]:
        nodes = []
        edges = []
        for node, data in self.G.nodes(data=True):
            nodes.append({'id': node, **data})
        for src, tgt in self.G.edges():
            edges.append({'source': src, 'target': tgt})
        return {'nodes': nodes, 'edges': edges}

def extract_skills(text: str, source: str) -> List[Dict[str, Any]]:
    prompt = f"""
Extract skills from the text. Each skill should have id, prereqs (list), mastery (0-100), confidence (0-1), citations (list).
Format as JSON list: [{{"id": "skill_name", "prereqs": ["prereq1"], "mastery": 50, "confidence": 0.8, "citations": ["source"]}}]

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