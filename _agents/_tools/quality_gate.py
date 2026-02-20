"""
Quality Gate Tool: Verifies research briefs against structural and content standards.
"""
import re
import sys

def parse_simple_yaml(text):
    """Simple parser for flat YAML frontmatter."""
    data = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data

def check_brief(filepath):
    """
    Checks a markdown brief for required headers, frontmatter, and word count.
    Returns a dict with 'passed' (bool), 'issues' (list), and 'metrics' (dict).
    """
    results = {
        "passed": True,
        "issues": [],
        "metrics": {}
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        results["passed"] = False
        results["issues"].append(f"Failed to read file: {e}")
        return results

    # 1. Check Frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    body = content

    if not frontmatter_match:
        results["passed"] = False
        results["issues"].append("Missing YAML frontmatter")
    else:
        try:
            fm_str = frontmatter_match.group(1)
            # Try to parse YAML using simple parser
            fm = parse_simple_yaml(fm_str)
            required_fm = ['Date', 'Author', 'Version', 'Status']
            for k in required_fm:
                if k not in fm:
                    results["passed"] = False
                    results["issues"].append(f"Missing frontmatter key: {k}")

            body = content[frontmatter_match.end():]
        except Exception as e:
            results["passed"] = False
            results["issues"].append(f"Invalid YAML frontmatter: {e}")

    # 2. Check Word Count
    # Simple word count
    words = body.split()
    word_count = len(words)
    results["metrics"]["word_count"] = word_count

    if word_count < 300:
        results["passed"] = False
        results["issues"].append(f"Word count too low: {word_count} (min 300)")

    # 3. Check Required Headers/Sections (Regex)
    required_patterns = [
        (r'^# ', "Title (H1)"),
        (r'\*\*Domain:\*\*', "Domain Metadata"),
        (r'## Executive Snapshot', "Executive Snapshot"),
        (r'## Deep Dives', "Deep Dives"),
        (r'## Relevance to BPR&D', "Relevance to BPR&D"),
        (r'## Actionable Recommendations', "Actionable Recommendations")
    ]

    for pattern, name in required_patterns:
        if not re.search(pattern, body, re.MULTILINE):
            results["passed"] = False
            results["issues"].append(f"Missing section: {name}")

    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        res = check_brief(filepath)
        if res['passed']:
            print(f"Checking {filepath}: PASSED")
            print(f"  Word count: {res['metrics']['word_count']}")
        else:
            print(f"Checking {filepath}: FAILED")
            for issue in res['issues']:
                print(f"  - {issue}")
    else:
        print("Usage: python quality_gate.py <filepath>")
