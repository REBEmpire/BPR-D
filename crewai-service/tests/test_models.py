import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.meeting import MeetingRequest, MeetingType

class TestModels(unittest.TestCase):
    def test_meeting_request(self):
        req = MeetingRequest(meeting_type="daily_briefing", agenda="Test")
        self.assertEqual(req.meeting_type, MeetingType.DAILY_BRIEFING)
        self.assertEqual(req.agenda, "Test")

if __name__ == '__main__':
    unittest.main()
