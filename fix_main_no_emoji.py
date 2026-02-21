with open("crewai-service/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove emoji
content = content.replace("⚡ ", "")

with open("crewai-service/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Removed emoji from main.py")
