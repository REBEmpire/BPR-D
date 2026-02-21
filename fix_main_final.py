import re

with open("crewai-service/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the specific block for trigger_special_session request creation
# We look for the pattern around the messed up quotes
pattern = re.compile(r'request = MeetingRequest\s*\(\s*meeting_type=MeetingType\.SPECIAL_SESSION,\s*participants=\["grok", "claude", "gemini", "abacus"\],\s*agenda=f""".*?GitHub Issue: #\{issue_num\}.*?\)\s*', re.DOTALL)

replacement = '''request = MeetingRequest(
        meeting_type=MeetingType.SPECIAL_SESSION,
        participants=["grok", "claude", "gemini", "abacus"],
        agenda=f"""**HiC Goal:** {topic}

GitHub Issue: #{issue_num}"""
    )
'''

# The regex might be hard to match perfectly with the messed up quotes.
# Let's try to just find the function and rewrite it?
# Or simple string replacement of the broken lines.

# Broken lines from grep:
# agenda=f"""**HiC Goal:** {topic}
# GitHub Issue: #{issue_num}"""""""
# )

broken_str = 'GitHub Issue: #{issue_num}"""""""'
fixed_str = 'GitHub Issue: #{issue_num}"""'

if broken_str in content:
    content = content.replace(broken_str, fixed_str)
    print("Fixed broken quotes.")
else:
    print("Broken quotes pattern not found (maybe already fixed or different?)")

# Also check for the issue_body one just in case
broken_body = 'Status: In Progress"""""""' # Assuming similar issue
if broken_body in content:
    content = content.replace(broken_body, 'Status: In Progress"""')
    print("Fixed broken body quotes.")

with open("crewai-service/main.py", "w", encoding="utf-8") as f:
    f.write(content)
