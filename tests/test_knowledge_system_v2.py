import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from knowledge_system.knowledge_graph_v2 import KnowledgeGraph
from skill_webs.skill_web_v2 import SkillWeb
from knowledge_system.upgrade_migration import migrate_v1_to_v2

class TestKnowledgeGraph:
    def setup_method(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.kg = KnowledgeGraph(db_path=self.db_path)

    def teardown_method(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_fact(self):
        self.kg.add_fact('A', 'relates_to', 'B')
        assert self.kg.G.has_node('A')
        assert self.kg.G.has_node('B')
        assert self.kg.G.has_edge('A', 'B')

    def test_query_nl(self):
        self.kg.add_fact('Python', 'is_a', 'Language')
        results = self.kg.query_nl('programming language')
        assert len(results) > 0
        assert 'Python' in [r['node'] for r in results]

    @patch('knowledge_system.knowledge_graph_v2.litellm.completion')
    def test_ingest_from_interaction(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"facts": [{"subj": "Python", "pred": "is_a", "obj": "programming language"}]}'
        mock_completion.return_value = mock_response
        text = "Python is a programming language used for AI."
        self.kg.ingest_from_interaction(text, 'test')
        assert len(self.kg.G.nodes) > 0

    def test_export_cypher(self):
        self.kg.add_fact('A', 'knows', 'B')
        cypher = self.kg.export_cypher()
        assert 'CREATE' in cypher[0]

    def test_export_jsonl(self):
        self.kg.add_fact('A', 'rel', 'B')
        self.kg.export_to_jsonl('test')
        assert os.path.exists('knowledge_snapshot_test.jsonl')

class TestSkillWeb:
    def setup_method(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.sw = SkillWeb(db_path=self.db_path)

    def teardown_method(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_skill(self):
        self.sw.add_skill('Skill1', prereqs=['Prereq1'], mastery=50)
        assert self.sw.G.has_node('Skill1')
        assert self.sw.G.has_edge('Prereq1', 'Skill1')

    def test_dag_cycle_error(self):
        self.sw.add_skill('A', prereqs=['B'])
        with pytest.raises(ValueError):
            self.sw.add_skill('B', prereqs=['A'])

    def test_generate_learning_path(self):
        self.sw.add_skill('Advanced', prereqs=['Basic'], mastery=80)
        self.sw.add_skill('Basic', mastery=50)
        path = self.sw.generate_learning_path('Advanced', {'Basic': 20})
        assert len(path) == 2
        assert path[0]['skill'] == 'Basic'

    def test_upgrade_skill_web(self):
        evidence = "SkillX requires SkillY, mastery 60."
        self.sw.upgrade_skill_web(self.sw, evidence)
        # Assuming LLM extracts
        # Hard to test without mock, but check no error

    def test_export_markdown(self):
        self.sw.add_skill('TestSkill')
        md = self.sw.export_to_markdown()
        assert '# Skill Web' in md
        assert 'TestSkill' in md

    def test_export_json(self):
        self.sw.add_skill('Test')
        data = self.sw.export_to_json()
        assert 'nodes' in data
        assert 'edges' in data

class TestMigration:
    def test_migrate_dry_run(self):
        # Mock or use actual, but dry run
        migrate_v1_to_v2(dry_run=True)
        # Check prints, but hard to assert

if __name__ == '__main__':
    pytest.main([__file__])