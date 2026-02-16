import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings

class TestConfig(unittest.TestCase):
    def test_keys_exist(self):
        # We assume .env is loaded
        self.assertIsNotNone(settings.GITHUB_REPO)
        self.assertEqual(settings.GITHUB_REPO, "REBEmpire/BPR-D")
        self.assertTrue(settings.XAI_API_KEY) # Should be set from .env

if __name__ == '__main__':
    unittest.main()
