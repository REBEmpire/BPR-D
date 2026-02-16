import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from crews.daily_briefing import create_daily_briefing_crew

class TestDailyBriefing(unittest.TestCase):
    def test_crew_creation(self):
        # This creates real agents so it needs API keys, which are in .env
        crew, meta = create_daily_briefing_crew(agenda="Test")
        self.assertEqual(meta["meeting_type"], "daily_briefing")
        self.assertIn("Co-Second in Command / Chief Strategist / Architect", meta["agents"]) # Role names
        # Check task count: 4 tasks
        self.assertEqual(len(crew.tasks), 4)

if __name__ == '__main__':
    unittest.main()
