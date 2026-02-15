import re

file_path = "web/src/components/quest-board.tsx"

with open(file_path, "r") as f:
    content = f.read()

# Add useMemo import if not present
if 'import { useMemo }' not in content:
    content = content.replace('import { CheckCircle2, Circle } from "lucide-react"', 'import { CheckCircle2, Circle } from "lucide-react"\nimport { useMemo } from "react"')

# Add optimization
# Find the line: const { isRussell, completedQuests, completeQuest } = useGamification()
# And insert the memoized set after it.
match = re.search(r'(const { isRussell, completedQuests, completeQuest } = useGamification\(\))', content)
if match:
    insertion = '\n\n  const completedIds = useMemo(() => new Set(completedQuests), [completedQuests])'
    content = content[:match.end()] + insertion + content[match.end():]

# Replace usage
content = content.replace('const isCompleted = completedQuests.includes(quest.id)', 'const isCompleted = completedIds.has(quest.id)')

with open(file_path, "w") as f:
    f.write(content)

print("Optimization applied.")
