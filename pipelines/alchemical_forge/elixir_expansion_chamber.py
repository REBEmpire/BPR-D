#!/usr/bin/env python3
"""
Elixir Expansion Chamber — Multi-turn content transmutation engine.

Transforms Jules Daily Briefs into fully expanded Elixirs (rich markdown content)
through a 4-6 turn alchemical process.

Alchemical Forge v1.1 — February 2026

Usage:
    python -m pipelines.alchemical_forge.elixir_expansion_chamber --dry-run --use-latest-brief
    python -m pipelines.alchemical_forge.elixir_expansion_chamber --output-format html --use-latest-brief
"""

import argparse
import asyncio
import json
import logging
import os
import re
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

# --- Version ---
VERSION = "1.1"

# --- Default Soul Stories (fallback) ---
DEFAULT_SOUL_STORIES = {
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

# --- Soul Stories Configuration ---
SOUL_STORIES_DEFAULT_PATH = SCRIPT_DIR / "soul_stories.json"


def load_soul_stories() -> dict:
    """Load soul stories from JSON config, with env var override support.

    Priority:
    1. SOUL_STORIES_PATH environment variable
    2. Default soul_stories.json in module directory
    3. Hardcoded defaults
    """
    # Check for env var override
    custom_path = os.environ.get("SOUL_STORIES_PATH")
    if custom_path:
        path = Path(custom_path)
    else:
        path = SOUL_STORIES_DEFAULT_PATH

    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
            # Remove _meta key if present
            stories = {k: v for k, v in data.items() if not k.startswith("_")}
            logger.debug(f"Loaded soul stories from: {path}")
            return stories
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load soul stories from {path}: {e}")

    logger.debug("Using default soul stories")
    return DEFAULT_SOUL_STORIES


# Load soul stories at module level
SOUL_STORIES = load_soul_stories()

# --- Paths ---
DRAFTS_DIR = PROJECT_ROOT / "publishing" / "hive" / "drafts"
OUTPUT_DIR = PROJECT_ROOT / "publishing" / "hive" / "elixirs"
LOGS_DIR = PROJECT_ROOT / "aether_logs"

# --- Output Format Converters ---

def convert_to_format(content: str, output_format: str) -> str:
    """Convert markdown content to the specified output format.

    Args:
        content: Markdown content
        output_format: One of 'md', 'html', 'notion'

    Returns:
        Converted content string
    """
    if output_format == "md":
        return content
    elif output_format == "html":
        return _convert_to_html(content)
    elif output_format == "notion":
        return _convert_to_notion(content)
    else:
        logger.warning(f"Unknown format '{output_format}', returning markdown")
        return content


def _convert_to_html(content: str) -> str:
    """Convert markdown to HTML.

    Uses the markdown library if available, otherwise falls back to basic regex.
    """
    try:
        import markdown
        html_body = markdown.markdown(
            content,
            extensions=['extra', 'nl2br', 'sane_lists']
        )
    except ImportError:
        # Fallback: basic regex-based conversion
        html_body = content
        # Headers
        html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
        # Bold and italic
        html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
        html_body = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_body)
        # Paragraphs
        html_body = re.sub(r'\n\n', '</p><p>', html_body)
        html_body = f'<p>{html_body}</p>'
        # Horizontal rules
        html_body = re.sub(r'<p>---</p>', '<hr>', html_body)

    # Wrap in HTML document
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transmuted Elixir</title>
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{ color: #1a1a2e; }}
        em {{ color: #6b5b95; }}
        hr {{ border: none; border-top: 2px solid #ddd; margin: 2rem 0; }}
        blockquote {{
            border-left: 4px solid #6b5b95;
            padding-left: 1rem;
            font-style: italic;
            color: #555;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
    return html_doc


def _convert_to_notion(content: str) -> str:
    """Convert markdown to Notion-compatible format.

    Notion accepts standard markdown but has some preferences:
    - Preserves most markdown syntax
    - Prefers explicit line breaks
    - Supports toggle blocks with > syntax
    """
    notion_content = content

    # Ensure double line breaks for paragraph separation
    notion_content = re.sub(r'\n(?!\n)', '\n\n', notion_content)

    # Add Notion metadata header
    notion_header = f"""---
notion_page_type: elixir
created_by: Alchemical Forge v{VERSION}
created_at: {datetime.utcnow().isoformat()}
---

"""
    return notion_header + notion_content


def get_soul_story_weave() -> str:
    """Generate the Soul Story Weave opening paragraph."""
    stories = SOUL_STORIES
    return f"""*In the ethereal workshop where {stories['grok']['name']} casts light upon hidden truths,
where {stories['claude']['name']} shapes raw thought into crystalline structures,
and {stories['gemini']['name']} races through infinite possibility spaces —
the Alchemist, {stories['abacus']['name']}, begins the Great Work.
Under the watchful eye of {stories['russell']['name']}, this Elixir is distilled.*

---

"""


def get_closing_transmutation() -> str:
    """Generate the closing transmutation signature."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""

---

*Transmuted by the Alchemist under the eye of the HiC Sovereign*
*{timestamp} | Alchemical Forge v{VERSION}*
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


def parse_raw_digest(content: str) -> dict:
    """Parse a Nightly Epstein Raw Digest into structured sections."""
    sections = {
        "title": "",
        "date": "",
        "intro": "", # New Material Ingested usually serves as intro context
        "topics": [], # Key Delta Insights will be mapped to topics
        "jules_take": "", # Anomalies / Follow-up Prompts
        "rabbit_hole": "", # Timeline Snippets
        "community": "", # Not present in raw digest
    }

    lines = content.split("\n")
    current_section = "intro"

    for line in lines:
        if line.startswith("# Epstein Raw Digest"):
            sections["title"] = line.strip()
            # Extract date if present
            match = re.search(r'–\s*(.*)', line)
            if match:
                sections["date"] = match.group(1).strip()
            continue

        if line.startswith("## New Material Ingested"):
            current_section = "intro"
            continue
        elif line.startswith("## Key Delta Insights"):
            current_section = "topics"
            continue
        elif line.startswith("## Updated Timeline Snippets"):
            current_section = "rabbit_hole"
            continue
        elif line.startswith("## New Anomalies"):
            current_section = "jules_take"
            continue

        if current_section == "intro":
            sections["intro"] += line + "\n"
        elif current_section == "topics":
            # Treat each bullet as a topic if possible, or just lump them
            if line.strip().startswith("- "):
                sections["topics"].append({"header": "Insight", "content": line.strip()})
            else:
                 # Append to previous topic if exists, else generic
                 if sections["topics"]:
                     sections["topics"][-1]["content"] += "\n" + line.strip()
        elif current_section == "rabbit_hole":
            sections["rabbit_hole"] += line + "\n"
        elif current_section == "jules_take":
            sections["jules_take"] += line + "\n"

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


async def transmute_brief(brief_content: str, turns: int = 4, dry_run: bool = False, mode: str = "standard") -> str:
    """Execute the multi-turn transmutation process."""
    logger.info(f"Beginning transmutation with {turns} turns (dry_run={dry_run}, mode={mode})")
    
    # Parse the brief based on mode
    if mode == "special-report":
        sections = parse_raw_digest(brief_content)
    else:
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
    output_format: str = "md",
    input_path: Optional[str] = None,
    mode: str = "standard",
    cumulative_paths: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> dict:
    """Run the Alchemical Forge transmutation pipeline.

    Args:
        dry_run: If True, don't commit changes or call live APIs
        use_latest_brief: Auto-find the most recent brief
        brief_path: Path to a specific brief file (legacy)
        turns: Number of expansion turns (1-6)
        output_format: Output format ('md', 'html', 'notion')
        input_path: Path to input file (overrides brief_path)
        mode: Transmutation mode
        cumulative_paths: Comma-separated list of paths for context
        output_dir: Custom output directory

    Returns:
        dict with success status, paths, grade, and errors
    """
    result = {
        "success": False,
        "brief_path": None,
        "elixir_path": None,
        "image_paths": [],
        "grade": None,
        "output_format": output_format,
        "errors": [],
    }
    
    # Determine output directory
    target_output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    target_output_dir.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find or validate the input
    source_path_str = input_path or brief_path
    if source_path_str:
        source = Path(source_path_str)
    elif use_latest_brief:
        source = find_latest_brief()
    else:
        source = find_latest_brief()
    
    if not source or not source.exists():
        error = f"Input not found: {source}"
        logger.error(error)
        result["errors"].append(error)
        return result
    
    result["brief_path"] = str(source)
    logger.info(f"Processing input: {source} (Mode: {mode})")
    
    # Read the brief/input
    brief_content = source.read_text()
    
    # Transmute the brief into an Elixir
    try:
        elixir_content = await transmute_brief(brief_content, turns=turns, dry_run=dry_run, mode=mode)
    except Exception as e:
        error = f"Transmutation failed: {e}"
        logger.error(error, exc_info=True)
        result["errors"].append(error)
        return result
    
    # Convert to requested format
    final_content = convert_to_format(elixir_content, output_format)

    # Determine file extension
    ext_map = {"md": ".md", "html": ".html", "notion": ".md"}
    extension = ext_map.get(output_format, ".md")

    # Generate output filename
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    elixir_filename = f"{date_str}-elixir{extension}"
    elixir_path = target_output_dir / elixir_filename
    
    # Write the Elixir
    if not dry_run:
        elixir_path.write_text(final_content)
        logger.info(f"Elixir written to: {elixir_path}")
    else:
        # In dry-run, write to drafts with "--dry-run" suffix
        dry_run_path = DRAFTS_DIR / f"{date_str}-elixir-dry-run{extension}"
        dry_run_path.write_text(final_content)
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
    
    # Run the grader (only grade markdown content, not HTML)
    try:
        from pipelines.alchemical_forge.verification.philosophers_stone_grader import grade_elixir
        grade_result = grade_elixir(elixir_content)  # Always grade the markdown version
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
        "version": VERSION,
        "dry_run": dry_run,
        "brief_path": result["brief_path"],
        "elixir_path": result["elixir_path"],
        "output_format": output_format,
        "grade": result["grade"],
        "turns": turns,
    }
    log_file = LOGS_DIR / f"forge-run-{date_str}.json"
    with open(log_file, "w") as f:
        json.dump(log_entry, f, indent=2)
    
    result["success"] = True
    logger.info(f"Alchemical Forge v{VERSION} transmutation complete!")
    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=f"Alchemical Forge v{VERSION} — Elixir Expansion Chamber",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run with latest brief (markdown output)
  python -m pipelines.alchemical_forge.elixir_expansion_chamber --dry-run --use-latest-brief
  
  # Full transmutation with HTML output
  python -m pipelines.alchemical_forge.elixir_expansion_chamber --use-latest-brief --output-format html

  # Notion-compatible output with specific brief
  python -m pipelines.alchemical_forge.elixir_expansion_chamber --brief publishing/hive/drafts/2026-02-15-hive-post.md --output-format notion
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
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["md", "html", "notion"],
        default="md",
        help="Output format: md (default), html, or notion",
    )
    parser.add_argument(
        "--input-path",
        type=str,
        help="Path to input file (alternative to --brief)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="standard",
        help="Transmutation mode (e.g., special-report)",
    )
    parser.add_argument(
        "--cumulative-paths",
        type=str,
        help="Comma-separated list of paths for context",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Custom output directory",
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
        output_format=args.output_format,
        input_path=args.input_path,
        mode=args.mode,
        cumulative_paths=args.cumulative_paths,
        output_dir=args.output_dir,
    ))
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"ALCHEMICAL FORGE v{VERSION} — TRANSMUTATION REPORT")
    print("=" * 60)
    print(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Brief: {result['brief_path']}")
    print(f"Elixir: {result['elixir_path']}")
    print(f"Format: {result['output_format']}")
    if result["grade"]:
        print(f"Grade: {result['grade'].get('total_score', 'N/A')}/100")
        print(f"Soul Resonance: {result['grade'].get('soul_resonance', 'N/A')}/20")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
    print("=" * 60)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
