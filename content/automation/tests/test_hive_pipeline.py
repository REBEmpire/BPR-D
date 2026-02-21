import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the pipelines/content directory to sys.path to import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../pipelines/content")))

# Import the module
# Since the filename has dots and dashes, we use importlib
import importlib.util
spec = importlib.util.spec_from_file_location("hive_pipeline", "pipelines/content/hive-pipeline-v0.1.py")
hive_pipeline = importlib.util.module_from_spec(spec)
sys.modules["hive_pipeline"] = hive_pipeline
spec.loader.exec_module(hive_pipeline)

class TestHivePipeline(unittest.TestCase):

    def test_parse_brief_success(self):
        """Test parsing a valid brief."""
        brief_content = """
# Daily Brief

**Key Findings**
- Finding 1
- Finding 2
- Finding 3
- Finding 4
- Finding 5

**Action Items**
- Do this
"""
        with patch("builtins.open", unittest.mock.mock_open(read_data=brief_content)):
            findings = hive_pipeline.parse_brief("dummy_path.md")
            self.assertIn("- Finding 1", findings)
            self.assertIn("- Finding 5", findings)

    def test_parse_brief_fallback(self):
        """Test fallback parsing when **Key Findings** header is missing."""
        brief_content = """
# Daily Brief

Key Findings
- Finding A
- Finding B

# Next Section
"""
        with patch("builtins.open", unittest.mock.mock_open(read_data=brief_content)):
            findings = hive_pipeline.parse_brief("dummy_path.md")
            self.assertIn("- Finding A", findings)

    def test_generate_hive_post_mock(self):
        """Test generating a post using mock mode."""
        content = "Test content"
        post = hive_pipeline.generate_hive_post(content, mock=True)
        self.assertIn("# The Hidden Grids", post)
        self.assertIn("<!-- IMAGE:", post)

    @patch("hive_pipeline.os.environ.get")
    def test_generate_hive_post_openai_missing(self, mock_env):
        """Test fallback to mock when OpenAI key is missing."""
        mock_env.return_value = None
        post = hive_pipeline.generate_hive_post("content")
        # Should return mock content
        self.assertIn("# The Hidden Grids", post)

if __name__ == "__main__":
    unittest.main()
