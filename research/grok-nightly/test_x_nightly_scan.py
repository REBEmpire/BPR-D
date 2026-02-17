import unittest
import sys
import os
from pathlib import Path

# Add the directory to sys.path to import the module
sys.path.append(str(Path(__file__).parent))

from x_nightly_scan import ConfigLoader, ContentAnalyzer

class TestGrokNightlyScan(unittest.TestCase):
    def setUp(self):
        self.keywords = ["AI", "Crypto", "BPR&D"]
        self.topics = {"Tech": ["AI", "Crypto"], "Internal": ["BPR&D"]}
        self.analyzer = ContentAnalyzer(self.keywords, self.topics)

    def test_analyzer_scoring(self):
        tweet = {
            "id": "1",
            "text": "This is a tweet about AI and BPR&D.",
            "public_metrics": {"like_count": 10, "retweet_count": 0}
        }
        results = self.analyzer.analyze([tweet])
        self.assertEqual(len(results), 1)
        # Matches: AI, BPR&D -> Score 2
        self.assertEqual(results[0]["score"], 2)
        self.assertEqual(results[0]["relevance"], "Medium")
        self.assertIn("ai", results[0]["matches"])
        self.assertIn("bpr&d", results[0]["matches"])

    def test_analyzer_high_engagement(self):
        tweet = {
            "id": "2",
            "text": "Just a random tweet.",
            "public_metrics": {"like_count": 2000, "retweet_count": 0}
        }
        results = self.analyzer.analyze([tweet])
        self.assertEqual(results[0]["score"], 2) # High engagement +2
        self.assertIn("high_engagement", results[0]["matches"])

    def test_analyzer_agent_mapping(self):
        tweet = {
            "id": "3",
            "text": "I love Python code.",
            "public_metrics": {}
        }
        results = self.analyzer.analyze([tweet])
        self.assertEqual(results[0]["suggested_agent"], "Gemini")

if __name__ == '__main__':
    unittest.main()
