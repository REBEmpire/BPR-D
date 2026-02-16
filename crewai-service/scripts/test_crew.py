import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from crews.daily_briefing import create_daily_briefing_crew, parse_crew_output

def test_daily_briefing():
    print("Initializing Daily Briefing Crew...")
    try:
        crew, metadata = create_daily_briefing_crew(agenda="Test run: Verify agent connectivity and JSON output.")
        print(f"Crew Metadata: {metadata}")

        print("\nKickoff! (This may take a minute)...")
        # Kickoff returns a CrewOutput object
        result = crew.kickoff()

        print("\n--- Raw Output ---")
        print(result.raw)

        print("\n--- Parsing Output ---")
        parsed = parse_crew_output(result.raw, "test-meeting-id")
        print(f"Success: {parsed.success}")
        print(f"Notes Length: {len(parsed.notes)}")
        print(f"Handoffs: {len(parsed.handoffs)}")
        print(f"Actions: {len(parsed.action_items)}")
        print(f"Decisions: {len(parsed.key_decisions)}")

        if parsed.handoffs:
            print("\nSample Handoff:", parsed.handoffs[0])

    except Exception as e:
        print(f"❌ Crew Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_daily_briefing()
