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
