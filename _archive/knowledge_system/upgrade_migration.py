#!/usr/bin/env python3
import os
import glob
import json
import argparse
from pathlib import Path
from knowledge_system.knowledge_graph_v2 import KnowledgeGraph, extract_knowledge
from skill_webs.skill_web_v2 import SkillWeb, extract_skills

def migrate_v1_to_v2(dry_run: bool = False):
    kg = KnowledgeGraph()
    sw = SkillWeb()

    # Glob v1 files
    v1_dirs = [
        '_shared/knowledge/**/*.md',
        '_shared/skills/**/*.md',
        '_shared/skill-graphs/**/*.md',
        '_agents/_shared/memories/**/*.md'
    ]

    all_files = []
    for pattern in v1_dirs:
        all_files.extend(glob.glob(pattern, recursive=True))

    print(f"Found {len(all_files)} v1 files to migrate.")

    for file_path in all_files:
        print(f"Processing {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract knowledge triples
            triples = extract_knowledge(content, file_path)
            for triple in triples:
                props = {'source': file_path, 'confidence': triple.get('confidence', 0.8)}
                if not dry_run:
                    kg.add_fact(triple['subj'], triple['pred'], triple['obj'], props)

            # Extract skills
            skills = extract_skills(content, file_path)
            for skill in skills:
                skill_id = skill['id']
                prereqs = skill.get('prereqs', [])
                mastery = skill.get('mastery', 0)
                confidence = skill.get('confidence', 0.5)
                citations = skill.get('citations', [file_path])
                if not dry_run:
                    sw.add_skill(skill_id, prereqs, mastery, confidence, citations)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if dry_run:
        print("Dry run complete. No changes made.")
        print(f"KG would have {len(kg.G.nodes)} nodes, {len(kg.G.edges)} edges")
        print(f"SW would have {len(sw.G.nodes)} nodes, {len(sw.G.edges)} edges")
    else:
        # Snapshot v1
        kg.export_to_jsonl('v1_migration')
        sw.export_to_markdown()  # or json
        print("Migration complete. Snapshots saved.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate v1 Knowledge/Skill system to v2')
    parser.add_argument('--dry-run', action='store_true', help='Run without making changes')
    args = parser.parse_args()
    migrate_v1_to_v2(dry_run=args.dry_run)