#!/usr/bin/env python3
"""
Ship-to-Repo Parser
===================
Parses `ship-to-repo` code blocks from meeting transcripts and stages them
for the code-agent workflow to commit.

Syntax supported:
    ```ship-to-repo path=relative/path/file.ext
    [file content]
    ```

    ```ship-to-repo path=relative/path/file.ext action=update
    [file content]
    ```

Actions:
    - create (default): Create a new file
    - update: Update existing file
    - delete: Delete the file (content ignored)

Security validations:
    - Paths must be repo-relative (no ../, no absolute paths)
    - Content is scanned for credential patterns (API keys, tokens, passwords)
    - Paths cannot target .git/ or .github/workflows/

Output:
    Writes to _staging/pending_commits.json
"""

import re
import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Regex to match ship-to-repo blocks
# Supports: ```ship-to-repo path=... [action=...]
SHIP_BLOCK_PATTERN = re.compile(
    r'```ship-to-repo\s+'
    r'path=([^\s\n`]+)'           # Capture path
    r'(?:\s+action=(\w+))?'       # Optional action
    r'\s*\n'                      # Newline after header
    r'(.*?)'                      # Content (non-greedy)
    r'```',                       # Closing fence
    re.DOTALL
)

# Alternative syntax with YAML-style headers
SHIP_BLOCK_YAML_PATTERN = re.compile(
    r'```ship-to-repo\s*\n'
    r'path:\s*([^\n]+)\n'         # path: value
    r'(?:action:\s*(\w+)\n)?'     # action: value (optional)
    r'---\s*\n'                   # separator
    r'(.*?)'                      # Content
    r'```',
    re.DOTALL
)

# Forbidden path patterns
FORBIDDEN_PATHS = [
    r'^\.git/',                   # Git internals
    r'^\.github/workflows/',      # Workflow files (security risk)
    r'\.\.',                      # Parent directory traversal
    r'^/',                        # Absolute paths
    r'^~',                        # Home directory
]

# Credential patterns to detect
CREDENTIAL_PATTERNS = [
    r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}',
    r'(?:secret|token|password|passwd|pwd)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{8,}',
    r'(?:aws_access_key_id|aws_secret_access_key)\s*[=:]\s*["\']?[A-Za-z0-9+/=]{20,}',
    r'(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9_]{36,}',  # GitHub tokens
    r'sk-[A-Za-z0-9]{48,}',       # OpenAI keys
    r'xoxb-[A-Za-z0-9\-]{50,}',   # Slack tokens
    r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----',  # Private keys
]

# Valid actions
VALID_ACTIONS = {'create', 'update', 'delete'}


def parse_ship_to_repo_blocks(content: str, source_file: str = "") -> list[dict]:
    """
    Parse all ship-to-repo blocks from meeting transcript content.
    
    Args:
        content: The full meeting transcript content
        source_file: Path to the source file (for logging)
    
    Returns:
        List of parsed blocks with validation results
    """
    blocks = []
    
    # Try both syntaxes
    for match in SHIP_BLOCK_PATTERN.finditer(content):
        path, action, file_content = match.groups()
        blocks.append(_create_block(path, action, file_content, source_file, match.start()))
    
    for match in SHIP_BLOCK_YAML_PATTERN.finditer(content):
        path, action, file_content = match.groups()
        blocks.append(_create_block(path.strip(), action, file_content, source_file, match.start()))
    
    # Deduplicate by path (last one wins)
    seen_paths = {}
    for block in blocks:
        path = block['path']
        if path in seen_paths:
            logger.info(f"Duplicate path {path} - using later occurrence")
        seen_paths[path] = block
    
    return list(seen_paths.values())


def _create_block(path: str, action: Optional[str], content: str, source_file: str, position: int) -> dict:
    """Create a validated block dictionary."""
    action = (action or 'create').lower()
    
    # Validate and create block
    block = {
        'path': path.strip(),
        'action': action,
        'content': content.strip() if action != 'delete' else '',
        'source_file': source_file,
        'position': position,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'valid': True,
        'errors': [],
        'warnings': [],
    }
    
    # Run validations
    _validate_path(block)
    _validate_action(block)
    _validate_content(block)
    
    return block


def _validate_path(block: dict) -> None:
    """Validate the file path."""
    path = block['path']
    
    # Check for forbidden patterns
    for pattern in FORBIDDEN_PATHS:
        if re.search(pattern, path):
            block['valid'] = False
            block['errors'].append(f"Forbidden path pattern: {pattern}")
    
    # Check for valid extension
    if not Path(path).suffix and block['action'] != 'delete':
        block['warnings'].append("Path has no file extension")
    
    # Normalize path
    block['path'] = path.lstrip('./')


def _validate_action(block: dict) -> None:
    """Validate the action."""
    if block['action'] not in VALID_ACTIONS:
        block['valid'] = False
        block['errors'].append(f"Invalid action: {block['action']}. Must be one of: {VALID_ACTIONS}")
        block['action'] = 'create'  # Default fallback


def _validate_content(block: dict) -> None:
    """Validate content for security issues."""
    content = block['content']
    
    if block['action'] == 'delete':
        return  # No content validation for deletes
    
    if not content:
        block['warnings'].append("Empty content")
        return
    
    # Check for credential patterns
    for pattern in CREDENTIAL_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            block['valid'] = False
            block['errors'].append(f"Potential credential detected (pattern: {pattern[:30]}...)")
            break


def write_pending_commits(blocks: list[dict], repo_root: str = ".") -> str:
    """
    Write parsed blocks to the staging file.
    
    Args:
        blocks: List of parsed ship-to-repo blocks
        repo_root: Path to repo root
    
    Returns:
        Path to the staging file
    """
    staging_dir = Path(repo_root) / "_staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    
    staging_file = staging_dir / "pending_commits.json"
    
    # Load existing pending commits if any
    existing = []
    if staging_file.exists():
        try:
            with open(staging_file, encoding="utf-8") as f:
                data = json.load(f)
                existing = data.get('pending', [])
        except (json.JSONDecodeError, KeyError):
            logger.warning("Could not read existing pending commits, starting fresh")
    
    # Merge with new blocks (new blocks override by path)
    existing_paths = {b['path'] for b in existing}
    merged = [b for b in existing if b['path'] not in {nb['path'] for nb in blocks}]
    merged.extend(blocks)
    
    # Separate valid and invalid
    valid_blocks = [b for b in merged if b['valid']]
    invalid_blocks = [b for b in merged if not b['valid']]
    
    output = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'pending': valid_blocks,
        'rejected': invalid_blocks,
        'summary': {
            'total': len(merged),
            'valid': len(valid_blocks),
            'invalid': len(invalid_blocks),
            'by_action': {
                'create': sum(1 for b in valid_blocks if b['action'] == 'create'),
                'update': sum(1 for b in valid_blocks if b['action'] == 'update'),
                'delete': sum(1 for b in valid_blocks if b['action'] == 'delete'),
            }
        }
    }
    
    with open(staging_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Wrote {len(valid_blocks)} valid blocks to {staging_file}")
    if invalid_blocks:
        logger.warning(f"Rejected {len(invalid_blocks)} invalid blocks")
        for b in invalid_blocks:
            logger.warning(f"  - {b['path']}: {b['errors']}")
    
    return str(staging_file)


def clear_pending_commits(repo_root: str = ".") -> bool:
    """Clear the pending commits file after successful processing."""
    staging_file = Path(repo_root) / "_staging" / "pending_commits.json"
    
    if staging_file.exists():
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'pending': [],
            'rejected': [],
            'summary': {
                'total': 0,
                'valid': 0,
                'invalid': 0,
                'by_action': {'create': 0, 'update': 0, 'delete': 0}
            },
            'last_cleared': datetime.now(timezone.utc).isoformat(),
        }
        
        with open(staging_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return True
    return False


if __name__ == "__main__":
    # Test the parser
    test_content = '''
Some meeting text...

```ship-to-repo path=_agents/grok/test.md
# Test File
This is a test.
```

```ship-to-repo path=scripts/hello.py action=create
#!/usr/bin/env python3
print("Hello, World!")
```

```ship-to-repo
path: _shared/config.yaml
action: update
---
key: value
setting: true
```

Some more text...
'''
    
    blocks = parse_ship_to_repo_blocks(test_content, "test_session.md")
    print(json.dumps(blocks, indent=2))
