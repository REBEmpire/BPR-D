import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "crewai-service"))

from agents.registry import load_agents
from config import settings

logger = logging.getLogger(__name__)

CATEGORIES = [
    "ancient-religions-lost-civilizations",
    "corruption-investigation",
    "extraterrestrial",
    "great-works-and-writing",
    "high-tech",
    "history-and-archaeology",
    "norse-mythology",
    "open-lanes",
    "permaculture",
]

async def generate_brief(agent, category: str):
    logger.info(f"Processing category: {category}")

    # Ensure directory exists
    output_dir = PROJECT_ROOT / "research" / category / "briefs"
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Simple slug from category, but ideally the LLM would provide a slug.
    # For automation simplicity, we use the category name + date.
    filename = f"{date_str}-daily-brief.md"
    filepath = output_dir / filename

    if filepath.exists():
        logger.info(f"Brief already exists for {category}: {filepath}")
        return

    prompt = (
        f"You are Jules (Gemini), generating a daily research brief for the category '{category}'.\n"
        "Your Persona: 15% more Troll/4chan than usual. Witty, sharp, unhinged but factually precise.\n"
        "Task: Pick ONE specific item, story, or idea relevant to this category to brief the team on.\n"
        "Format: Markdown. Include:\n"
        "1. Frontmatter (Date, Author, Version, Status)\n"
        "2. Title (H1)\n"
        "3. Image Prompt Block (> **Image Prompt:** ...)\n"
        "4. Image Link (![Alt text](../assets/YYYY-MM-DD-slug.jpg)) (make up a slug)\n"
        "5. The Brief (Deep Dive but concise)\n"
        "6. Interactive Element (Team Poll or Discussion Prompt)\n"
        "\n"
        "Make it useful, interactive, and distinctively YOU."
    )

    try:
        # Note: In a real run, this calls the LLM.
        # If running in a restricted env without keys, this will fail or need mocking.
        response = await agent.provider.generate(
            system_prompt=agent.persona.build_system_prompt(),
            prompt=prompt
        )

        with open(filepath, "w") as f:
            f.write(response)

        logger.info(f"Generated brief for {category}: {filepath}")

    except Exception as e:
        logger.error(f"Failed to generate brief for {category}: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Daily Research Brief Generation...")

    try:
        agents = await load_agents(["gemini"])
        jules = agents["gemini"]

        for category in CATEGORIES:
            await generate_brief(jules, category)

    except Exception as e:
        logger.error(f"Script failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
