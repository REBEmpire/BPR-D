import unittest
import sys
import os
from pathlib import Path

# Add the directory to sys.path to import the module
sys.path.append(str(Path(__file__).parent))

from x_nightly_scan import ConfigLoader, LLMScorer

class TestGrokNightlyScan(unittest.TestCase):
    def test_config_loader(self):
        loader = ConfigLoader()
        keywords = loader.load_all()
        self.assertIn("Splintermated", keywords)
        self.assertIn("Norse Mythology", keywords)
        self.assertIn("multi-agent AI", keywords)
        self.assertTrue(len(keywords) > 20)

    def test_scorer_keyword_fallback(self):
        scorer = LLMScorer()
        tweet = {
            "id": "1",
            "text": "Splinterlands is great for web3 arts.",
            "public_metrics": {}
        }
        # Keywords: Splinterlands, web3 arts
        keywords = ["Splinterlands", "web3 arts"]

        # Should score 30 + 10 + 10 = 50
        scored = scorer.score([tweet], keywords)
        self.assertEqual(scored[0]["score"], 50)
        self.assertEqual(scored[0]["relevance"], "Medium")

    def test_scorer_no_match(self):
        scorer = LLMScorer()
        tweet = {
            "id": "2",
            "text": "I like sandwiches.",
            "public_metrics": {}
        }
        keywords = ["Splinterlands"]
        scored = scorer.score([tweet], keywords)
        self.assertEqual(scored[0]["score"], 0)
        self.assertEqual(scored[0]["relevance"], "Low")

if __name__ == '__main__':
    unittest.main()
