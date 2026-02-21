import re

with open("crewai-service/main.py", "r") as f:
    content = f.read()

# Fix issue_body multiline f-string
content = content.replace(
    'issue_body = f"Triggered by {hic_id} via Dashboard.',
    'issue_body = f"""Triggered by {hic_id} via Dashboard.'
)
content = content.replace(
    'Status: In Progress"',
    'Status: In Progress"""'
)

# Fix agenda multiline f-string
content = content.replace(
    'agenda=f"**⚡ HiC Goal:** {topic}',
    'agenda=f"""**⚡ HiC Goal:** {topic}'
)
content = content.replace(
    'GitHub Issue: #{issue_num}"',
    'GitHub Issue: #{issue_num}"""'
)

with open("crewai-service/main.py", "w") as f:
    f.write(content)
