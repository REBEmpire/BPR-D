from meetings.daily_briefing import DailyBriefing
from meetings.work_session import WorkSession
from meetings.special_session import SpecialSession

MEETING_TYPES = {
    "daily_briefing": DailyBriefing,
    "work_session": WorkSession,
    "special_session": SpecialSession,
}
