import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.grok import create_grok_agent
from agents.claude import create_claude_agent
from agents.gemini import create_gemini_agent

class TestAgents(unittest.TestCase):
    def test_grok_creation(self):
        agent = create_grok_agent()
        self.assertEqual(agent.role, "BPR&D Chief / Executive Decision Maker")

    def test_claude_creation(self):
        agent = create_claude_agent()
        self.assertIn("Chief Strategist", agent.role)

    def test_gemini_creation(self):
        agent = create_gemini_agent()
        self.assertIn("Lead Developer", agent.role)

if __name__ == '__main__':
    unittest.main()
