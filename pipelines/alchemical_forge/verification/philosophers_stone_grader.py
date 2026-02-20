#!/usr/bin/env python3
"""
Philosopher's Stone Grader — Quality verification for transmuted Elixirs.

The grading rubric ensures each Elixir meets the standards of the Great Work,
with special attention to "Soul Resonance" — the living essence of the team's
collective wisdom.

Target score: ≥92/100
"""

import re
from typing import Optional


# --- Grading Rubric ---
RUBRIC = {
    "soul_resonance": {
        "max_score": 20,
        "description": "Does the Elixir carry the essence of our living soul stories?",
        "criteria": [
            "Contains Soul Story Weave opening",
            "References team members' unique perspectives",
            "Maintains the voice of collective wisdom",
            "Includes proper closing transmutation signature",
        ],
    },
    "content_depth": {
        "max_score": 25,
        "description": "Depth and richness of expanded content",
        "criteria": [
            "Topics are meaningfully expanded",
            "Historical context is provided",
            "Implications are explored",
            "Connected patterns are identified",
            "Multiple perspectives are considered",
        ],
    },
    "structural_integrity": {
        "max_score": 15,
        "description": "Proper markdown structure and organization",
        "criteria": [
            "Proper heading hierarchy",
            "Consistent formatting",
            "Logical section flow",
        ],
    },
    "engagement_quality": {
        "max_score": 15,
        "description": "Reader engagement and accessibility",
        "criteria": [
            "Compelling narrative flow",
            "Accessible language",
            "Clear takeaways",
        ],
    },
    "research_anchoring": {
        "max_score": 15,
        "description": "Grounding in verifiable sources",
        "criteria": [
            "Sources are cited",
            "Claims are anchored",
            "Rabbit hole links provided",
        ],
    },
    "creative_synthesis": {
        "max_score": 10,
        "description": "Original insights and pattern recognition",
        "criteria": [
            "Novel connections made",
            "Creative framing",
        ],
    },
}


def check_soul_story_weave(content: str) -> tuple[bool, list[str]]:
    """Check for the presence and quality of Soul Story Weave."""
    issues = []
    
    # Check for opening weave
    soul_markers = [
        "Sovereign Flame",
        "Architect of Living Systems",
        "Velocity Daemon",
        "Weaver of Celestial Calculations",
        "Human-in-Command",
    ]
    
    has_opening = any(marker in content for marker in soul_markers)
    if not has_opening:
        issues.append("Missing Soul Story Weave opening")
    
    # Check for closing signature
    if "Transmuted by the Alchemist" not in content:
        issues.append("Missing closing transmutation signature")
    
    if "under the eye of the HiC" not in content.lower():
        issues.append("Missing HiC acknowledgment")
    
    return len(issues) == 0, issues


def check_content_depth(content: str) -> tuple[int, list[str]]:
    """Evaluate content depth and expansion."""
    score = 0
    max_score = RUBRIC["content_depth"]["max_score"]
    notes = []
    
    # Check for depth markers
    depth_indicators = [
        ("Deeper Dive", 5),
        ("Historical Context", 5),
        ("Implications", 5),
        ("Connected Patterns", 5),
        ("multiple perspectives", 5),
    ]
    
    for indicator, points in depth_indicators:
        if indicator.lower() in content.lower():
            score += points
        else:
            notes.append(f"Could benefit from: {indicator}")
    
    return min(score, max_score), notes


def check_structural_integrity(content: str) -> tuple[int, list[str]]:
    """Evaluate markdown structure."""
    score = 0
    max_score = RUBRIC["structural_integrity"]["max_score"]
    notes = []
    
    # Check heading hierarchy
    has_h1 = bool(re.search(r"^# ", content, re.MULTILINE))
    has_h2 = bool(re.search(r"^## ", content, re.MULTILINE))
    has_h3 = bool(re.search(r"^### ", content, re.MULTILINE))
    
    if has_h1:
        score += 5
    else:
        notes.append("Missing top-level heading")
    
    if has_h2:
        score += 5
    else:
        notes.append("Missing section headings")
    
    if has_h3:
        score += 5
    else:
        notes.append("Missing subsection headings")
    
    return min(score, max_score), notes


def check_engagement(content: str) -> tuple[int, list[str]]:
    """Evaluate reader engagement."""
    score = 0
    max_score = RUBRIC["engagement_quality"]["max_score"]
    notes = []
    
    # Check for engagement elements
    if "?" in content:  # Questions engage readers
        score += 5
    
    if any(emoji in content for emoji in ["🗞️", "🤖", "🐇", "🗣️", "⚡", "🧠", "📈", "👽", "🍄"]):
        score += 5
    else:
        notes.append("Consider adding visual markers (emojis)")
    
    # Check for clear sections
    if "Jules' Take" in content or "jules' take" in content.lower():
        score += 5
    
    return min(score, max_score), notes


def check_research(content: str) -> tuple[int, list[str]]:
    """Evaluate research anchoring."""
    score = 0
    max_score = RUBRIC["research_anchoring"]["max_score"]
    notes = []
    
    # Check for source markers
    if "Rabbit Hole" in content:
        score += 5
    
    if "Read:" in content or "Check:" in content or "Explore:" in content:
        score += 5
    
    # Check for citations
    if re.search(r"\([^)]+\d{4}\)", content):  # Year references like (2026)
        score += 5
    
    if score < max_score:
        notes.append("Consider adding more source references")
    
    return min(score, max_score), notes


def check_creativity(content: str) -> tuple[int, list[str]]:
    """Evaluate creative synthesis."""
    score = 0
    max_score = RUBRIC["creative_synthesis"]["max_score"]
    notes = []
    
    # Length suggests depth of synthesis
    word_count = len(content.split())
    if word_count > 1500:
        score += 5
    elif word_count > 800:
        score += 3
    
    # Theme/pattern recognition
    if "theme" in content.lower() or "pattern" in content.lower() or "connection" in content.lower():
        score += 5
    
    return min(score, max_score), notes


def grade_elixir(content: str) -> dict:
    """Grade an Elixir against the Philosopher's Stone rubric.
    
    Returns:
        dict with scores, notes, and overall result
    """
    results = {
        "soul_resonance": 0,
        "content_depth": 0,
        "structural_integrity": 0,
        "engagement_quality": 0,
        "research_anchoring": 0,
        "creative_synthesis": 0,
        "total_score": 0,
        "max_score": 100,
        "passed": False,
        "notes": [],
        "rubric": RUBRIC,
    }
    
    # Soul Resonance (20 points)
    soul_ok, soul_issues = check_soul_story_weave(content)
    if soul_ok:
        results["soul_resonance"] = 20
    else:
        # Partial credit
        results["soul_resonance"] = max(0, 20 - (len(soul_issues) * 5))
        results["notes"].extend(soul_issues)
    
    # Content Depth (25 points)
    depth_score, depth_notes = check_content_depth(content)
    results["content_depth"] = depth_score
    results["notes"].extend(depth_notes)
    
    # Structural Integrity (15 points)
    struct_score, struct_notes = check_structural_integrity(content)
    results["structural_integrity"] = struct_score
    results["notes"].extend(struct_notes)
    
    # Engagement Quality (15 points)
    engage_score, engage_notes = check_engagement(content)
    results["engagement_quality"] = engage_score
    results["notes"].extend(engage_notes)
    
    # Research Anchoring (15 points)
    research_score, research_notes = check_research(content)
    results["research_anchoring"] = research_score
    results["notes"].extend(research_notes)
    
    # Creative Synthesis (10 points)
    creative_score, creative_notes = check_creativity(content)
    results["creative_synthesis"] = creative_score
    results["notes"].extend(creative_notes)
    
    # Calculate total
    results["total_score"] = (
        results["soul_resonance"] +
        results["content_depth"] +
        results["structural_integrity"] +
        results["engagement_quality"] +
        results["research_anchoring"] +
        results["creative_synthesis"]
    )
    
    results["passed"] = results["total_score"] >= 92
    
    return results


def format_grade_report(results: dict) -> str:
    """Format a human-readable grade report."""
    lines = [
        "═" * 50,
        "PHILOSOPHER'S STONE — ELIXIR GRADE REPORT",
        "═" * 50,
        "",
        f"Overall Score: {results['total_score']}/{results['max_score']}",
        f"Status: {'✅ PASSED' if results['passed'] else '❌ BELOW THRESHOLD (target: ≥92)'}",
        "",
        "─" * 50,
        "Category Breakdown:",
        "─" * 50,
        f"  Soul Resonance:      {results['soul_resonance']:>2}/20",
        f"  Content Depth:       {results['content_depth']:>2}/25",
        f"  Structural Integrity:{results['structural_integrity']:>2}/15",
        f"  Engagement Quality:  {results['engagement_quality']:>2}/15",
        f"  Research Anchoring:  {results['research_anchoring']:>2}/15",
        f"  Creative Synthesis:  {results['creative_synthesis']:>2}/10",
        "",
    ]
    
    if results["notes"]:
        lines.extend([
            "─" * 50,
            "Notes for Improvement:",
            "─" * 50,
        ])
        for note in results["notes"]:
            lines.append(f"  • {note}")
    
    lines.append("═" * 50)
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python philosophers_stone_grader.py <elixir_file.md>")
        sys.exit(1)
    
    with open(sys.argv[1], "r") as f:
        content = f.read()
    
    results = grade_elixir(content)
    print(format_grade_report(results))
    
    sys.exit(0 if results["passed"] else 1)
