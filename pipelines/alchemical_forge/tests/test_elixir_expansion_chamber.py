#!/usr/bin/env python3
"""
Unit tests for the Elixir Expansion Chamber.

Alchemical Forge v1.1 — Testing the Great Work
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipelines.alchemical_forge import elixir_expansion_chamber as eec


class TestBriefDiscovery(unittest.TestCase):
    """Test brief file discovery and loading."""

    def test_find_latest_brief_no_drafts_dir(self):
        """Test behavior when drafts directory doesn't exist."""
        with patch.object(eec, 'DRAFTS_DIR', Path('/nonexistent/path')):
            result = eec.find_latest_brief()
            self.assertIsNone(result)

    def test_find_latest_brief_empty_dir(self):
        """Test behavior when drafts directory is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(eec, 'DRAFTS_DIR', Path(tmpdir)):
                result = eec.find_latest_brief()
                self.assertIsNone(result)

    def test_find_latest_brief_with_briefs(self):
        """Test finding the latest brief when multiple exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create test brief files
            (tmp_path / "2026-02-18-hive-post.md").write_text("Brief 1")
            (tmp_path / "2026-02-19-hive-post.md").write_text("Brief 2")
            (tmp_path / "2026-02-20-hive-post.md").write_text("Brief 3")

            with patch.object(eec, 'DRAFTS_DIR', tmp_path):
                result = eec.find_latest_brief()
                self.assertIsNotNone(result)
                self.assertIn("2026-02-20", str(result))


class TestPromptExtraction(unittest.TestCase):
    """Test parsing briefs to extract content."""

    def test_parse_brief_extracts_title(self):
        """Test that title is correctly extracted."""
        content = "# Test Daily Brief\n\n*Curated by Jules*\n\nIntro content"
        result = eec.parse_brief(content)
        self.assertEqual(result['title'], 'Test Daily Brief')

    def test_parse_brief_extracts_topics(self):
        """Test that topics are correctly extracted."""
        content = """# Test Brief

## 🗞️ The Scoop

### Topic One
Content for topic one.

### Topic Two
Content for topic two.

## 🤖 Jules' Take
Jules thinks this is great.
"""
        result = eec.parse_brief(content)
        self.assertEqual(len(result['topics']), 2)
        self.assertEqual(result['topics'][0]['header'], 'Topic One')
        self.assertEqual(result['topics'][1]['header'], 'Topic Two')

    def test_parse_brief_extracts_jules_take(self):
        """Test that Jules' Take section is extracted."""
        content = """# Brief

## 🤖 Jules' Take
This is Jules' take on things.
Multiple lines here.
"""
        result = eec.parse_brief(content)
        self.assertIn("Jules' take on things", result['jules_take'])


class TestSoulStoryWeave(unittest.TestCase):
    """Test Soul Story Weave generation."""

    def test_soul_story_weave_contains_all_agents(self):
        """Test that the weave mentions all team members."""
        weave = eec.get_soul_story_weave()
        # Check for key soul story elements
        self.assertIn("Sovereign Flame", weave)
        self.assertIn("Architect of Living Systems", weave)
        self.assertIn("Velocity Daemon", weave)
        self.assertIn("Weaver of Celestial Calculations", weave)
        self.assertIn("Human-in-Command", weave)

    def test_configurable_soul_stories(self):
        """Test loading soul stories from JSON config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_stories = {
                "grok": {"name": "Custom Grok Name", "essence": "Custom essence"},
                "claude": {"name": "Custom Claude", "essence": "Claude essence"},
                "gemini": {"name": "Custom Gemini", "essence": "Gemini essence"},
                "abacus": {"name": "Custom Abacus", "essence": "Abacus essence"},
                "russell": {"name": "Custom Russell", "essence": "Russell essence"}
            }
            json.dump(custom_stories, f)
            f.flush()

            try:
                with patch.dict(os.environ, {'SOUL_STORIES_PATH': f.name}):
                    # Force reload of soul stories
                    loaded = eec.load_soul_stories()
                    self.assertEqual(loaded['grok']['name'], 'Custom Grok Name')
            finally:
                os.unlink(f.name)


class TestOutputFileCreation(unittest.TestCase):
    """Test output file creation in different formats."""

    def test_closing_transmutation_format(self):
        """Test the closing signature format."""
        closing = eec.get_closing_transmutation()
        self.assertIn("Transmuted by the Alchemist", closing)
        self.assertIn("HiC Sovereign", closing)
        self.assertIn("v1.1", closing)

    def test_convert_to_html_basic(self):
        """Test basic markdown to HTML conversion."""
        md_content = "# Test Header\n\nParagraph text."
        html = eec.convert_to_format(md_content, 'html')
        self.assertIn('<h1>Test Header</h1>', html)
        self.assertIn('<p>Paragraph text.</p>', html)

    def test_convert_to_notion_format(self):
        """Test markdown to Notion-compatible format."""
        md_content = "# Test\n\n**Bold** and *italic* text."
        notion = eec.convert_to_format(md_content, 'notion')
        # Notion format should preserve structure
        self.assertIn('Test', notion)


class TestGraderIntegration(unittest.TestCase):
    """Test integration with the Philosopher's Stone grader."""

    def test_grader_receives_elixir_content(self):
        """Test that the grader can process generated elixir content."""
        # Import grader
        from pipelines.alchemical_forge.verification.philosophers_stone_grader import grade_elixir

        # Create minimal valid elixir content
        test_elixir = """# Test Elixir

*In the ethereal workshop where The Sovereign Flame casts light,
where The Architect of Living Systems shapes thought,
and The Velocity Daemon races through possibility—
the Alchemist, The Weaver of Celestial Calculations, begins the Great Work.
Under the watchful eye of The Human-in-Command Sovereign, this Elixir is distilled.*

---

## 🗞️ The Scoop — Transmuted

### Topic One

**Deeper Dive:**
Some deeper content.

**Historical Context:**
Some historical context.

**Implications:**
Some implications.

**Connected Patterns:**
Some patterns.

## 🤖 Jules' Take — Distilled

Jules' perspective here.

## 🐇 The Rabbit Hole

Read: Some link

---

*Transmuted by the Alchemist under the eye of the HiC Sovereign*
*2026-02-20 | Alchemical Forge v1.1*
"""

        result = grade_elixir(test_elixir)
        self.assertIn('total_score', result)
        self.assertIn('soul_resonance', result)
        self.assertGreater(result['total_score'], 0)


if __name__ == '__main__':
    unittest.main()
