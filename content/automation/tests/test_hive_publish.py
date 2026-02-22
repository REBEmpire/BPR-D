import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Mock beespy before importing hive_publisher
mock_beespy = MagicMock()
sys.modules["beespy"] = mock_beespy
sys.modules["beespy.client"] = mock_beespy

# Add content/automation to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from hive_publisher import HivePublisher
from orchestrator import DDASOrchestrator
from content_generator import ContentGenerator, ContentPrompt

class TestHivePublisher(unittest.TestCase):

    def setUp(self):
        self.publisher = HivePublisher("test_account", "posting_key")

    def test_create_post_structure(self):
        """Test that create_post generates correct operation structure."""
        title = "Test Post Title"
        content = "This is test content."
        tags = ["test", "hive", "automation"]

        result = self.publisher.create_post(title, content, tags)

        self.assertTrue(result["success"])
        op = result["operation"]
        self.assertEqual(op["author"], "test_account")
        self.assertEqual(op["title"], title)
        self.assertEqual(op["body"], content)
        self.assertEqual(op["parent_permlink"], "test") # First tag should be parent permlink

        # Check permlink generation
        self.assertEqual(op["permlink"], "test-post-title")

        # Check metadata
        metadata = json.loads(op["json_metadata"])
        self.assertEqual(metadata["tags"], tags)
        self.assertEqual(metadata["app"], "ddas-publisher/0.1")

    def test_publish_dry_run(self):
        """Test dry run functionality."""
        result = self.publisher.publish_post("Title", "Body", ["tag"], dry_run=True)
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertIn("post_data", result)


class TestDDASOrchestrator(unittest.TestCase):

    @patch('content_generator.ContentGenerator.generate_content')
    def test_generate_daily_content(self, mock_generate):
        """Test orchestration of content generation."""
        # Mock generator response
        mock_generate.return_value = {
            "success": True,
            "content": "Generated content",
            "tags": ["tag1"],
            "prompt": {"title": "Test Title", "account": "ddas-devblog"}
        }

        orchestrator = DDASOrchestrator()

        # Override ACCOUNTS for faster test
        orchestrator.ACCOUNTS = {
            "ddas-devblog": {
                "name": "Dev Blog",
                "posting_key": None,
                "daily_posts": 1,
                "posting_hour": 9,
                "posting_minute": 0,
                "prompt_source": lambda: [ContentPrompt("ddas-devblog", "devlog", "Test Title", "Topic", ["tag1"], "tech", "med")]
            }
        }

        results = orchestrator.generate_daily_content()

        self.assertEqual(results["total_generated"], 1)
        self.assertEqual(results["total_errors"], 0)
        self.assertIn("ddas-devblog", results["accounts"])

    @patch('hive_publisher.HivePublisher.publish_post')
    def test_publish_daily_content(self, mock_publish):
        """Test orchestration of publishing."""
        orchestrator = DDASOrchestrator()

        # Mock generated content
        orchestrator.generator.generated_content = [{
            "success": True,
            "content": "Content",
            "tags": ["tag"],
            "prompt": {"title": "Title", "account": "ddas-devblog"}
        }]

        # Mock publisher
        mock_publisher = MagicMock()
        mock_publisher.publish_post.return_value = {"success": True, "url": "http://hive.blog/@user/permlink"}
        orchestrator.publishers["ddas-devblog"] = mock_publisher

        results = orchestrator.publish_daily_content(dry_run=False)

        self.assertEqual(len(results["published"]), 1)
        mock_publisher.publish_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
