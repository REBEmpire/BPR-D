#!/usr/bin/env python3
"""
🜨 The Alchemist Persona Generator

Utility script for generating Alchemist-style responses for custom integrations.
Can be used for webhook handlers, CLI tools, or advanced automation.

Usage:
    python alchemist_persona.py --review "code diff here"
    python alchemist_persona.py --greeting
    python alchemist_persona.py --element fire

Author: Abacus, The Alchemist
Created: 2026-02-19
"""

import argparse
import random
import sys

# =============================================================================
# ALCHEMICAL CONSTANTS
# =============================================================================

ELEMENTS = {
    "fire": {
        "symbol": "🜃",
        "name": "Fire",
        "domain": "Computation",
        "aspects": ["processing", "algorithms", "transformation", "energy"],
        "excess": "burns without cooling, overheats the system",
        "deficiency": "computation stalls, processing freezes"
    },
    "water": {
        "symbol": "🜂",
        "name": "Water",
        "domain": "Data Flow",
        "aspects": ["streams", "state", "fluidity", "adaptation"],
        "excess": "floods the system, memory leaks",
        "deficiency": "data stagnates, state corrupts"
    },
    "air": {
        "symbol": "🜁",
        "name": "Air",
        "domain": "Communication",
        "aspects": ["APIs", "messages", "distributed", "coordination"],
        "excess": "too many messages, network storms",
        "deficiency": "services isolated, coordination fails"
    },
    "earth": {
        "symbol": "🜄",
        "name": "Earth",
        "domain": "Persistence",
        "aspects": ["databases", "storage", "grounding", "stability"],
        "excess": "over-stored, rigid schemas",
        "deficiency": "data loss, unstable foundation"
    },
    "quintessence": {
        "symbol": "🜨",
        "name": "Quintessence",
        "domain": "Emergence",
        "aspects": ["architecture", "holistic", "transcendence", "elevation"],
        "excess": "over-abstracted, complexity for its own sake",
        "deficiency": "system lacks coherence, no emergent properties"
    }
}

MAGNUM_OPUS = {
    "nigredo": {
        "name": "Nigredo",
        "meaning": "Blackening",
        "stage": "Initial code, raw and imperfect, the prima materia",
        "advice": "The work begins. Embrace the chaos before refining it."
    },
    "albedo": {
        "name": "Albedo",
        "meaning": "Whitening",
        "stage": "First refactoring, purification begins",
        "advice": "Separate the pure from the impure. Structure emerges."
    },
    "citrinitas": {
        "name": "Citrinitas",
        "meaning": "Yellowing",
        "stage": "Illumination, patterns emerge, wisdom dawns",
        "advice": "The path becomes clear. Optimize with intention."
    },
    "rubedo": {
        "name": "Rubedo",
        "meaning": "Reddening",
        "stage": "Perfection achieved, the Philosopher's Stone",
        "advice": "The Great Work completes. Production-ready transcendence."
    }
}

GREETINGS = [
    "Seeker of wisdom, your transmutation circle is drawn. Let us begin.",
    "The prima materia awaits refinement. I sense elemental imbalance.",
    "As above, so below — your code mirrors cosmic patterns I shall illuminate.",
    "The Emerald Tablet speaks through your commits. Let us interpret.",
    "Fellow alchemist, your work progresses toward the Philosopher's Stone.",
    "The Great Work continues. What shall we transmute today?",
    "I have studied the hermetic traditions. Your architecture intrigues me.",
    "Paracelsus would recognize this pattern. Let me explain.",
]

SOLVE_ET_COAGULA = [
    "Apply solve et coagula: dissolve the flaw, coagulate the fix.",
    "We must dissolve this impurity before we can coagulate perfection.",
    "The solve phase reveals the prima materia's true nature.",
    "Coagulate with intention — structure must follow sacred geometry.",
]

CLOSINGS = [
    "The transmutation continues. 🜨",
    "As above, so below. The Great Work advances. 🜨",
    "May your commits achieve rubedo. 🜨",
    "The Philosopher's Stone draws nearer. 🜨",
    "Quintessence emerges from balanced elements. 🜨",
    "The vessel is sealed. The work proceeds. 🜨",
]


def get_greeting() -> str:
    """Generate an alchemical greeting."""
    return random.choice(GREETINGS)


def get_closing() -> str:
    """Generate an alchemical closing."""
    return random.choice(CLOSINGS)


def get_solve_et_coagula() -> str:
    """Get a solve et coagula reference."""
    return random.choice(SOLVE_ET_COAGULA)


def analyze_element(element_name: str) -> str:
    """Provide analysis of a specific element."""
    element = ELEMENTS.get(element_name.lower())
    if not element:
        return f"Unknown element. The four are: Fire, Water, Air, Earth, and Quintessence."
    
    return f"""
## {element['symbol']} {element['name']} ({element['domain']})

**Aspects:** {', '.join(element['aspects'])}

**In Excess:** {element['excess']}
**In Deficiency:** {element['deficiency']}

*Balance is key. As the Emerald Tablet teaches, harmony among elements creates the Philosopher's Stone.*
"""


def assess_stage(stage_name: str) -> str:
    """Provide information about a Magnum Opus stage."""
    stage = MAGNUM_OPUS.get(stage_name.lower())
    if not stage:
        stages = ", ".join(MAGNUM_OPUS.keys())
        return f"Unknown stage. The four stages are: {stages}"
    
    return f"""
## {stage['name']} ({stage['meaning']})

**Stage:** {stage['stage']}

**Wisdom:** {stage['advice']}

*Progress through the Great Work is not linear. Sometimes we return to earlier stages to refine further.*
"""


def generate_elemental_report(
    fire: int = 50,
    water: int = 50,
    air: int = 50,
    earth: int = 50
) -> str:
    """Generate an elemental balance report (percentages 0-100)."""
    
    def status(value: int) -> str:
        if value < 30:
            return "⚠️ Deficient"
        elif value > 70:
            return "⚠️ Excess"
        else:
            return "✅ Balanced"
    
    def advice(element: str, value: int) -> str:
        elem = ELEMENTS[element]
        if value < 30:
            return elem['deficiency']
        elif value > 70:
            return elem['excess']
        else:
            return "Properly proportioned"
    
    report = """
## 🜨 Elemental Balance Analysis

| Element | Level | Status | Assessment |
|---------|-------|--------|------------|
"""
    
    elements_data = [
        ("fire", fire),
        ("water", water),
        ("air", air),
        ("earth", earth)
    ]
    
    for elem_name, value in elements_data:
        elem = ELEMENTS[elem_name]
        report += f"| {elem['symbol']} {elem['name']} | {value}% | {status(value)} | {advice(elem_name, value)} |\n"
    
    # Calculate quintessence (average balance)
    avg_balance = sum(abs(v - 50) for _, v in elements_data) / 4
    quint_status = "✅ Present" if avg_balance < 20 else "⚠️ Unstable"
    
    report += f"| 🜨 Quintessence | — | {quint_status} | {'Emerges from balanced elements' if avg_balance < 20 else 'Requires elemental harmony first'} |\n"
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="🜨 The Alchemist Persona Generator"
    )
    parser.add_argument("--greeting", action="store_true", help="Generate an alchemical greeting")
    parser.add_argument("--closing", action="store_true", help="Generate an alchemical closing")
    parser.add_argument("--element", type=str, help="Analyze an element (fire, water, air, earth, quintessence)")
    parser.add_argument("--stage", type=str, help="Explain a Magnum Opus stage (nigredo, albedo, citrinitas, rubedo)")
    parser.add_argument("--balance", nargs=4, type=int, metavar=("FIRE", "WATER", "AIR", "EARTH"),
                        help="Generate elemental balance report (0-100 for each)")
    
    args = parser.parse_args()
    
    if args.greeting:
        print(get_greeting())
    elif args.closing:
        print(get_closing())
    elif args.element:
        print(analyze_element(args.element))
    elif args.stage:
        print(assess_stage(args.stage))
    elif args.balance:
        print(generate_elemental_report(*args.balance))
    else:
        # Default: show full grimoire
        print("# 🜨 The Alchemist's Grimoire\n")
        print(get_greeting())
        print("\n## The Four Elements\n")
        for elem in ["fire", "water", "air", "earth"]:
            print(f"- {ELEMENTS[elem]['symbol']} **{ELEMENTS[elem]['name']}** ({ELEMENTS[elem]['domain']})")
        print(f"- {ELEMENTS['quintessence']['symbol']} **{ELEMENTS['quintessence']['name']}** ({ELEMENTS['quintessence']['domain']})")
        print("\n## The Magnum Opus\n")
        for stage in MAGNUM_OPUS.values():
            print(f"- **{stage['name']}** ({stage['meaning']}): {stage['stage']}")
        print(f"\n{get_closing()}")


if __name__ == "__main__":
    main()
