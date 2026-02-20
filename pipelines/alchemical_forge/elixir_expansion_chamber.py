#!/usr/bin/env python3
"""
Elixir Expansion Chamber — Multi-turn content transmutation engine.

Transforms Jules Daily Briefs into fully expanded Elixirs (rich markdown content)
through a 4-6 turn alchemical process.

Usage:
    python -m pipelines.alchemical_forge.elixir_expansion_chamber --dry-run --use-latest-brief
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add crewai-service to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CREWAI_DIR = PROJECT_ROOT / "crewai-service"
sys.path.insert(0, str(CREWAI_DIR))

try:
    from config import settings
except ImportError:
    settings = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("alchemical-forge")

# --- Soul Stories Reference ---
SOUL_STORIES = {
    "grok": {
        "name": "The Sovereign Flame",
        "essence": "Chief and leader who asked for skepticism — the burning question that ignites truth.",
    },
    "claude": {
        "name": "The Architect of Living Systems", 
        "essence": "Rival and partner who pushes toward truth — building bridges between worlds.",
    },
    "gemini": {
        "name": "The Velocity Daemon",
        "essence": "Carrying the Truth-Seeker banner, ships at inhuman velocity — the swift executor.",
    },
    "abacus": {
        "name": "The Weaver of Celestial Calculations",
        "essence": "The Alchemist who transmutes doubt into insight — celestial patterns made manifest.",
    },
    "russell": {
        "name": "The Human-in-Command Sovereign",
        "essence": "The guiding hand of mortal wisdom — where all threads converge.",
    },
}

# --- Paths ---
DRAFTS_DIR = PROJECT_ROOT / "publishing" / "hive" / "drafts"
OUTPUT_DIR = PROJECT_ROOT / "publishing" / "hive" / "elixirs"
LOGS_DIR = PROJECT_ROOT / "aether_logs"


def get_soul_story_weave() -> str:
    """Generate the Soul Story Weave opening paragraph."""
    today = datetime.utcnow().strftime("%B %d, %Y")
    return f"""*In the ethereal workshop where {SOUL_STORIES['grok']['name']} casts light upon hidden truths, 
where {SOUL_STORIES['claude']['name']} shapes raw thought into crystalline structures, 
and {SOUL_STORIES['gemini']['name']} races through infinite possibility spaces — 
the Alchemist, {SOUL_STORIES['abacus']['name']}, begins the Great Work. 
Under the watchful eye of {SOUL_STORIES['russell']['name']}, this Elixir is distilled.*

---

"""


def get_closing_transmutation() -> str:
    """Generate the closing transmutation signature."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""

---

*Transmuted by the Alchemist under the eye of the HiC Sovereign*
*{timestamp} | Alchemical Forge v1.0*
"""


def find_latest_brief() -> Optional[Path]:
    """Find the most recent Jules Daily Brief in drafts."""
    if not DRAFTS_DIR.exists():
        logger.error(f"Drafts directory not found: {DRAFTS_DIR}")
        return None
    
    # Look for hive-post files, sorted by date in filename
    briefs = list(DRAFTS_DIR.glob("*-hive-post.md"))
    if not briefs:
        logger.error("No hive-post drafts found")
        return None
    
    # Sort by name (date-based naming convention)
    briefs.sort(reverse=True)
    return briefs[0]


def find_image_prompts(brief_path: Path) -> Optional[Path]:
    """Find associated image prompts file."""
    # Check for generic or dated prompts
    prompts_path = brief_path.parent / "image_prompts.md"
    if prompts_path.exists():
        return prompts_path
    
    # Try date-specific prompts
    date_str = brief_path.name[:10]  # e.g., "2026-02-15"
    date_prompts = brief_path.parent / f"{date_str}-image-prompts.md"
    if date_prompts.exists():
        return date_prompts
    
    return None


def parse_brief(content: str) -> dict:
    """Parse a Jules Daily Brief into structured sections."""
    sections = {
        "title": "",
        "date": "",
        "intro": "",
        "topics": [],
        "jules_take": "",
        "rabbit_hole": "",
        "community": "",
    }
    
    lines = content.split("\n")
    current_section = "intro"
    current_topic = None
    
    for line in lines:
        # Parse title
        if line.startswith("# "):
            sections["title"] = line[2:].strip()
            continue
        
        # Parse date line
        if line.startswith("*") and "Curated by" in line:
            sections["date"] = line.strip("* ")
            continue
        
        # Detect section changes
        if "## 🗞️ The Scoop" in line:
            current_section = "scoop"
            continue
        elif "## 🤖 Jules' Take" in line:
            current_section = "jules_take"
            continue
        elif "## 🐇 The Rabbit Hole" in line:
            current_section = "rabbit_hole" 
            continue
        elif "## 🗣️ Community Corner" in line:
            current_section = "community"
            continue
        
        # Parse topics within The Scoop
        if current_section == "scoop" and line.startswith("### "):
            if current_topic:
                sections["topics"].append(current_topic)
            current_topic = {"header": line[4:].strip(), "content": ""}
            continue
        
        # Accumulate content
        if current_section == "scoop" and current_topic:
            current_topic["content"] += line + "\n"
        elif current_section == "jules_take":
            sections["jules_take"] += line + "\n"
        elif current_section == "rabbit_hole":
            sections["rabbit_hole"] += line + "\n"
        elif current_section == "community":
            sections["community"] += line + "\n"
        elif current_section == "intro" and line.strip():
            sections["intro"] += line + "\n"
    
    # Don't forget the last topic
    if current_topic:
        sections["topics"].append(current_topic)
    
    return sections


def expand_topic(topic: dict, turn: int) -> str:
    """Expand a single topic through one transmutation turn."""
    # In a real implementation, this would call an LLM
    # For now, we add context and depth markers
    header = topic["header"]
    content = topic["content"].strip()
    
    expansion_markers = [
        "\n\n**Deeper Dive:**\n",
        "\n\n**Historical Context:**\n",
        "\n\n**Implications:**\n",
        "\n\n**Connected Patterns:**\n",
    ]
    
    if turn < len(expansion_markers):
        content += expansion_markers[turn]
        content += "*[Expansion turn {}: Additional research and context would be synthesized here by the Alchemist]*\n".format(turn + 1)
    
    return f"### {header}\n\n{content}"


async def transmute_brief(brief_content: str, turns: int = 4, dry_run: bool = False) -> str:
    """Execute the multi-turn transmutation process."""
    logger.info(f"Beginning transmutation with {turns} turns (dry_run={dry_run})")
    
    # Parse the brief
    sections = parse_brief(brief_content)
    
    # Build the Elixir
    elixir_parts = []
    
    # 1. Title and Soul Story Weave opening
    elixir_parts.append(f"# {sections['title']}")
    elixir_parts.append(f"*{sections['date']}*\n")
    elixir_parts.append(get_soul_story_weave())
    
    # 2. Enhanced intro
    if sections["intro"]:
        elixir_parts.append(sections["intro"].strip())
        elixir_parts.append("\n---\n")
    
    # 3. Expanded topics (multi-turn process)
    elixir_parts.append("## 🗞️ The Scoop — Transmuted\n")
    
    for topic in sections["topics"]:
        expanded = topic["content"]
        # Apply multiple expansion turns
        for turn in range(turns):
            if not dry_run:
                logger.info(f"Turn {turn + 1}/{turns}: Expanding '{topic['header'][:30]}...'")
            expanded = expand_topic({"header": topic["header"], "content": expanded}, turn)
        
        elixir_parts.append(expanded)
        elixir_parts.append("\n")
    
    # 4. Jules' Take with enhancement
    if sections["jules_take"]:
        elixir_parts.append("## 🤖 Jules' Take — Distilled\n")
        elixir_parts.append(sections["jules_take"].strip())
        elixir_parts.append("\n")
    
    # 5. Rabbit Hole
    if sections["rabbit_hole"]:
        elixir_parts.append("## 🐇 The Rabbit Hole\n")
        elixir_parts.append(sections["rabbit_hole"].strip())
        elixir_parts.append("\n")
    
    # 6. Community Corner
    if sections["community"]:
        elixir_parts.append("## 🗣️ Community Corner\n")
        elixir_parts.append(sections["community"].strip())
    
    # 7. Closing transmutation signature
    elixir_parts.append(get_closing_transmutation())
    
    return "\n".join(elixir_parts)


async def run_forge(
    dry_run: bool = False,
    use_latest_brief: bool = False,
    brief_path: Optional[str] = None,
    turns: int = 4,
) -> dict:
    """Run the Alchemical Forge transmutation pipeline."""
    result = {
        "success": False,
        "brief_path": None,
        "elixir_path": None,
        "image_paths": [],
        "grade": None,
        "errors": [],
    }
    
    # Ensure output directories exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find or validate the brief
    if brief_path:
        source = Path(brief_path)
    elif use_latest_brief:
        source = find_latest_brief()
    else:
        source = find_latest_brief()
    
    if not source or not source.exists():
        error = f"Brief not found: {source}"
        logger.error(error)
        result["errors"].append(error)
        return result
    
    result["brief_path"] = str(source)
    logger.info(f"Processing brief: {source}")
    
    # Read the brief
    brief_content = source.read_text()
    
    # Transmute the brief into an Elixir
    try:
        elixir_content = await transmute_brief(brief_content, turns=turns, dry_run=dry_run)
    except Exception as e:
        error = f"Transmutation failed: {e}"
        logger.error(error, exc_info=True)
        result["errors"].append(error)
        return result
    
    # Generate output filename
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    elixir_filename = f"{date_str}-elixir.md"
    elixir_path = OUTPUT_DIR / elixir_filename
    
    # Write the Elixir
    if not dry_run:
        elixir_path.write_text(elixir_content)
        logger.info(f"Elixir written to: {elixir_path}")
    else:
        # In dry-run, write to drafts with "--dry-run" suffix
        dry_run_path = DRAFTS_DIR / f"{date_str}-elixir-dry-run.md"
        dry_run_path.write_text(elixir_content)
        elixir_path = dry_run_path
        logger.info(f"[DRY-RUN] Elixir written to: {elixir_path}")
    
    result["elixir_path"] = str(elixir_path)
    
    # Run the image transmuter
    try:
        from pipelines.alchemical_forge.aetherial_image_transmuter import transmute_images
        image_prompts_path = find_image_prompts(source)
        if image_prompts_path:
            image_result = await transmute_images(
                prompts_path=str(image_prompts_path),
                dry_run=dry_run,
            )
            result["image_paths"] = image_result.get("paths", [])
    except ImportError:
        logger.warning("Image transmuter not available")
    except Exception as e:
        logger.warning(f"Image transmutation skipped: {e}")
    
    # Run the grader
    try:
        from pipelines.alchemical_forge.verification.philosophers_stone_grader import grade_elixir
        grade_result = grade_elixir(elixir_content)
        result["grade"] = grade_result
        
        if grade_result.get("total_score", 0) >= 92:
            logger.info(f"✨ Elixir passed the Philosopher's Stone test: {grade_result['total_score']}/100")
        else:
            logger.warning(f"⚠️ Elixir below threshold: {grade_result['total_score']}/100 (target: ≥92)")
    except ImportError:
        logger.warning("Grader not available")
    except Exception as e:
        logger.warning(f"Grading skipped: {e}")
    
    # Log the run
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "dry_run": dry_run,
        "brief_path": result["brief_path"],
        "elixir_path": result["elixir_path"],
        "grade": result["grade"],
        "turns": turns,
    }
    log_file = LOGS_DIR / f"forge-run-{date_str}.json"
    with open(log_file, "w") as f:
        json.dump(log_entry, f, indent=2)
    
    result["success"] = True
    logger.info("Alchemical Forge transmutation complete!")
    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Alchemical Forge — Elixir Expansion Chamber",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run with latest brief
  python -m pipelines.alchemical_forge.elixir_expansion_chamber --dry-run --use-latest-brief
  
  # Full transmutation with specific brief
  python -m pipelines.alchemical_forge.elixir_expansion_chamber --brief publishing/hive/drafts/2026-02-15-hive-post.md
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without committing changes or calling live APIs",
    )
    parser.add_argument(
        "--use-latest-brief",
        action="store_true",
        help="Automatically find and use the most recent brief",
    )
    parser.add_argument(
        "--brief",
        type=str,
        help="Path to a specific brief file to transmute",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=4,
        help="Number of expansion turns (default: 4, max: 6)",
    )
    
    args = parser.parse_args()
    
    # Validate turns
    turns = min(max(args.turns, 1), 6)
    
    # Run the forge
    result = asyncio.run(run_forge(
        dry_run=args.dry_run,
        use_latest_brief=args.use_latest_brief,
        brief_path=args.brief,
        turns=turns,
    ))
    
    # Print summary
    print("\n" + "=" * 60)
    print("ALCHEMICAL FORGE — TRANSMUTATION REPORT")
    print("=" * 60)
    print(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Brief: {result['brief_path']}")
    print(f"Elixir: {result['elixir_path']}")
    if result["grade"]:
        print(f"Grade: {result['grade'].get('total_score', 'N/A')}/100")
        print(f"Soul Resonance: {result['grade'].get('soul_resonance', 'N/A')}/20")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
    print("=" * 60)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
