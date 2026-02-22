"""Transcript Parser - Extracts action items, decisions, code snippets, and references."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import yaml


@dataclass
class ActionItem:
    """Represents an extracted action item from a meeting transcript."""
    raw_text: str
    line_number: int
    speaker: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0
    item_type: str = "task"  # task, decision, blocker, code_snippet, reference


@dataclass
class Decision:
    """Represents a decision made during the meeting."""
    raw_text: str
    line_number: int
    speaker: Optional[str] = None
    context: Optional[str] = None
    keywords: List[str] = field(default_factory=list)


@dataclass
class CodeSnippet:
    """Represents a code snippet mentioned in the meeting."""
    code: str
    language: Optional[str] = None
    line_number: int = 0
    context: Optional[str] = None


@dataclass
class MeetingMetadata:
    """Metadata extracted from meeting transcript."""
    meeting_id: str
    date: str
    time: Optional[str] = None
    duration_minutes: Optional[int] = None
    participants: List[Dict[str, str]] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    source_file: str = ""


@dataclass
class ParsedTranscript:
    """Complete parsed result from a meeting transcript."""
    metadata: MeetingMetadata
    action_items: List[ActionItem]
    decisions: List[Decision]
    code_snippets: List[CodeSnippet]
    raw_content: str


class TranscriptParser:
    """Parses meeting transcripts to extract actionable items."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        extraction_config = config.get('mcd', {}).get('extraction', {})
        self.min_confidence = extraction_config.get('min_confidence', 0.7)
        self.action_patterns = extraction_config.get('action_patterns', [
            r"will implement", r"will create", r"will update", r"will fix",
            r"will add", r"will review", r"will research", r"let's make sure",
            r"we need to", r"TODO:", r"ACTION:", r"TASK:", r"@\w+ will"
        ])
        self.decision_patterns = extraction_config.get('decision_patterns', [
            r"we decided", r"agreed to", r"final decision", r"DECISION:", r"approved"
        ])
        self.deadline_patterns = extraction_config.get('deadline_patterns', [
            r"by (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"by end of (week|month|day|sprint)",
            r"due (\d{4}-\d{2}-\d{2})",
            r"deadline:? (\d{4}-\d{2}-\d{2})",
            r"by (\d{1,2})/(\d{1,2})"
        ])
        
        # Agent name patterns
        self.agent_patterns = [
            r"@(\w+)",
            r"(claude|grok|abacus|gemini|perplexity|russell)",
        ]
    
    def parse(self, transcript_path: str) -> ParsedTranscript:
        """Parse a meeting transcript file."""
        path = Path(transcript_path)
        if not path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")
        
        content = path.read_text(encoding='utf-8')
        
        # Extract YAML frontmatter if present
        metadata = self._extract_metadata(content, str(path))
        
        # Get the main content (after frontmatter)
        main_content = self._get_main_content(content)
        
        # Extract all items
        action_items = self._extract_action_items(main_content)
        decisions = self._extract_decisions(main_content)
        code_snippets = self._extract_code_snippets(main_content)
        
        return ParsedTranscript(
            metadata=metadata,
            action_items=action_items,
            decisions=decisions,
            code_snippets=code_snippets,
            raw_content=content
        )
    
    def _extract_metadata(self, content: str, source_file: str) -> MeetingMetadata:
        """Extract YAML frontmatter metadata."""
        # Check for YAML frontmatter
        yaml_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
        
        if yaml_match:
            try:
                yaml_content = yaml.safe_load(yaml_match.group(1))
                return MeetingMetadata(
                    meeting_id=yaml_content.get('meeting_id', self._generate_meeting_id(source_file)),
                    date=str(yaml_content.get('date', datetime.now().strftime('%Y-%m-%d'))),
                    time=yaml_content.get('time'),
                    duration_minutes=yaml_content.get('duration_minutes'),
                    participants=yaml_content.get('participants', []),
                    topics_discussed=yaml_content.get('topics_discussed', []),
                    source_file=source_file
                )
            except yaml.YAMLError:
                pass
        
        # Generate metadata from filename and content
        return MeetingMetadata(
            meeting_id=self._generate_meeting_id(source_file),
            date=datetime.now().strftime('%Y-%m-%d'),
            source_file=source_file
        )
    
    def _generate_meeting_id(self, source_file: str) -> str:
        """Generate meeting ID from source file path."""
        path = Path(source_file)
        stem = path.stem
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"meeting-{date_str}-{stem}"
    
    def _get_main_content(self, content: str) -> str:
        """Get content after YAML frontmatter."""
        yaml_match = re.match(r'^---\n.+?\n---\n?', content, re.DOTALL)
        if yaml_match:
            return content[yaml_match.end():]
        return content
    
    def _extract_action_items(self, content: str) -> List[ActionItem]:
        """Extract action items from content."""
        items = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            line_lower = line.lower()
            
            # Check each action pattern
            for pattern in self.action_patterns:
                if re.search(pattern.lower(), line_lower):
                    item = self._create_action_item(line, line_num)
                    if item.confidence >= self.min_confidence:
                        items.append(item)
                    break  # Only match once per line
        
        return items
    
    def _create_action_item(self, text: str, line_number: int) -> ActionItem:
        """Create an ActionItem from a line of text."""
        # Extract speaker if present (format: "Speaker: text" or "**Speaker**: text")
        speaker = None
        speaker_match = re.match(r'^[\*]*([A-Za-z]+)[\*]*:\s*', text)
        if speaker_match:
            speaker = speaker_match.group(1)
        
        # Extract assignee
        assignee = self._extract_assignee(text)
        
        # Extract deadline
        deadline = self._extract_deadline(text)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text, assignee, deadline, keywords)
        
        return ActionItem(
            raw_text=text.strip(),
            line_number=line_number,
            speaker=speaker,
            assignee=assignee,
            deadline=deadline,
            keywords=keywords,
            confidence=confidence,
            item_type="task"
        )
    
    def _extract_assignee(self, text: str) -> Optional[str]:
        """Extract assigned agent from text."""
        text_lower = text.lower()
        
        # Check for @mentions first
        mention_match = re.search(r'@(\w+)', text)
        if mention_match:
            return mention_match.group(1).lower()
        
        # Check for agent names followed by "will"
        for agent in ['claude', 'grok', 'abacus', 'gemini', 'perplexity', 'russell']:
            if re.search(rf'{agent}[,\s]+(will|should|needs to|must)', text_lower):
                return agent
        
        return None
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract deadline from text."""
        text_lower = text.lower()
        today = datetime.now()
        
        # Check for explicit date format
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if date_match:
            return date_match.group(1)
        
        # Check for "end of week"
        if 'end of week' in text_lower or 'by friday' in text_lower:
            # Calculate next Friday
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            deadline = today + timedelta(days=days_until_friday)
            return deadline.strftime('%Y-%m-%d')
        
        # Check for "end of month"
        if 'end of month' in text_lower:
            if today.month == 12:
                deadline = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                deadline = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return deadline.strftime('%Y-%m-%d')
        
        # Check for day names
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if f'by {day}' in text_lower:
                days_ahead = (i - today.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                deadline = today + timedelta(days=days_ahead)
                return deadline.strftime('%Y-%m-%d')
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Technical terms to look for
        tech_keywords = [
            'api', 'database', 'frontend', 'backend', 'test', 'deploy', 'docker',
            'kubernetes', 'aws', 'github', 'ci/cd', 'pipeline', 'documentation',
            'security', 'authentication', 'rate limiting', 'cache', 'performance',
            'bug', 'fix', 'feature', 'refactor', 'review', 'merge', 'branch',
            'config', 'environment', 'script', 'automation', 'monitoring'
        ]
        
        keywords = []
        text_lower = text.lower()
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _calculate_confidence(self, text: str, assignee: Optional[str], 
                             deadline: Optional[str], keywords: List[str]) -> float:
        """Calculate confidence score for an action item."""
        confidence = 0.5  # Base confidence
        
        # Boost for having an assignee
        if assignee:
            confidence += 0.2
        
        # Boost for having a deadline
        if deadline:
            confidence += 0.15
        
        # Boost for technical keywords
        confidence += min(len(keywords) * 0.05, 0.15)
        
        # Boost for explicit action markers
        text_lower = text.lower()
        if any(marker in text_lower for marker in ['todo:', 'action:', 'task:']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_decisions(self, content: str) -> List[Decision]:
        """Extract decisions from content."""
        decisions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            line_lower = line.lower()
            
            for pattern in self.decision_patterns:
                if re.search(pattern.lower(), line_lower):
                    # Get context (surrounding lines)
                    start_idx = max(0, line_num - 3)
                    end_idx = min(len(lines), line_num + 2)
                    context = '\n'.join(lines[start_idx:end_idx])
                    
                    # Extract speaker
                    speaker = None
                    speaker_match = re.match(r'^[\*]*([A-Za-z]+)[\*]*:\s*', line)
                    if speaker_match:
                        speaker = speaker_match.group(1)
                    
                    decisions.append(Decision(
                        raw_text=line.strip(),
                        line_number=line_num,
                        speaker=speaker,
                        context=context,
                        keywords=self._extract_keywords(line)
                    ))
                    break
        
        return decisions
    
    def _extract_code_snippets(self, content: str) -> List[CodeSnippet]:
        """Extract code snippets from content."""
        snippets = []
        
        # Match fenced code blocks
        code_pattern = r'```(\w+)?\n(.+?)```'
        matches = re.finditer(code_pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1)
            code = match.group(2).strip()
            
            # Find line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Get surrounding context
            lines = content.split('\n')
            context_start = max(0, line_number - 3)
            context = '\n'.join(lines[context_start:line_number])
            
            snippets.append(CodeSnippet(
                code=code,
                language=language,
                line_number=line_number,
                context=context
            ))
        
        return snippets


# ============================================================================
# Ship-to-Repo Parsing (integrated from ship_to_repo_parser.py)
# ============================================================================
# 
# Parses `ship-to-repo` code blocks from meeting transcripts and stages them
# for the code-agent workflow to commit.
#
# Syntax supported:
#     ```ship-to-repo path=relative/path/file.ext
#     [file content]
#     ```
#
#     ```ship-to-repo path=relative/path/file.ext action=update
#     [file content]
#     ```
#
# Actions:
#     - create (default): Create a new file
#     - update: Update existing file
#     - delete: Delete the file (content ignored)
#
# Security validations:
#     - Paths must be repo-relative (no ../, no absolute paths)
#     - Content is scanned for credential patterns (API keys, tokens, passwords)
#     - Paths cannot target .git/ or .github/workflows/
#
# Output:
#     Writes to _staging/pending_commits.json

import json
import logging
from datetime import timezone

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


def parse_ship_to_repo_blocks(content: str, source_file: str = "") -> List[Dict[str, Any]]:
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
        blocks.append(_create_ship_block(path, action, file_content, source_file, match.start()))
    
    for match in SHIP_BLOCK_YAML_PATTERN.finditer(content):
        path, action, file_content = match.groups()
        blocks.append(_create_ship_block(path.strip(), action, file_content, source_file, match.start()))
    
    # Deduplicate by path (last one wins)
    seen_paths = {}
    for block in blocks:
        path = block['path']
        if path in seen_paths:
            logger.info(f"Duplicate path {path} - using later occurrence")
        seen_paths[path] = block
    
    return list(seen_paths.values())


def _create_ship_block(path: str, action: Optional[str], content: str, source_file: str, position: int) -> Dict[str, Any]:
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
    _validate_ship_path(block)
    _validate_ship_action(block)
    _validate_ship_content(block)
    
    return block


def _validate_ship_path(block: Dict[str, Any]) -> None:
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


def _validate_ship_action(block: Dict[str, Any]) -> None:
    """Validate the action."""
    if block['action'] not in VALID_ACTIONS:
        block['valid'] = False
        block['errors'].append(f"Invalid action: {block['action']}. Must be one of: {VALID_ACTIONS}")
        block['action'] = 'create'  # Default fallback


def _validate_ship_content(block: Dict[str, Any]) -> None:
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


def write_pending_commits(blocks: List[Dict[str, Any]], repo_root: str = ".") -> str:
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
