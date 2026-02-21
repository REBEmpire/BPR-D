"""Code Generator - Generates code files, documentation, or task files based on extracted content."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .parser import ActionItem, CodeSnippet, Decision
from .skill_linker import SkillLinkResult


@dataclass
class GeneratedFile:
    """Represents a file to be generated."""
    path: str
    content: str
    file_type: str  # 'code', 'documentation', 'task', 'config'
    description: str
    source_line: Optional[int] = None


@dataclass
class GenerationResult:
    """Result of code generation."""
    files: List[GeneratedFile]
    documentation_updates: List[Dict[str, Any]]
    warnings: List[str]
    summary: str


class CodeGenerator:
    """Generates code files and documentation from meeting extractions."""
    
    def __init__(self, config: Dict[str, Any], repo_root: str = "."):
        self.config = config
        self.repo_root = Path(repo_root)
        self.templates_dir = self.repo_root / '_shared' / 'templates'
    
    def generate_from_code_snippets(self, snippets: List[CodeSnippet], 
                                     meeting_id: str) -> List[GeneratedFile]:
        """Generate code files from extracted code snippets."""
        files = []
        
        for i, snippet in enumerate(snippets):
            if not snippet.code.strip():
                continue
            
            # Determine file extension from language
            ext = self._get_extension(snippet.language)
            filename = f"generated-{meeting_id}-snippet-{i + 1}{ext}"
            
            # Add header comment
            header = self._generate_code_header(snippet, meeting_id)
            content = f"{header}\n\n{snippet.code}"
            
            files.append(GeneratedFile(
                path=f"_agents/meeting-code-deployer/generated/{filename}",
                content=content,
                file_type='code',
                description=f"Code snippet from meeting (line {snippet.line_number})",
                source_line=snippet.line_number
            ))
        
        return files
    
    def generate_documentation(self, action_items: List[ActionItem],
                               decisions: List[Decision],
                               skill_links: Dict[int, SkillLinkResult],
                               meeting_id: str,
                               meeting_date: str) -> GeneratedFile:
        """Generate a meeting summary documentation file."""
        content = self._build_meeting_summary(
            action_items, decisions, skill_links, meeting_id, meeting_date
        )
        
        return GeneratedFile(
            path=f"meetings/summaries/{meeting_id}-summary.md",
            content=content,
            file_type='documentation',
            description="Auto-generated meeting summary"
        )
    
    def generate_action_docs(self, action_items: List[ActionItem],
                             skill_links: Dict[int, SkillLinkResult],
                             meeting_id: str) -> List[GeneratedFile]:
        """Generate individual action item documentation."""
        files = []
        
        for action in action_items:
            skill_link = skill_links.get(action.line_number)
            doc_content = self._build_action_doc(action, skill_link, meeting_id)
            
            if doc_content:
                # Use a sanitized version of the action for filename
                safe_name = self._sanitize_filename(action.raw_text[:40])
                filename = f"action-{action.line_number}-{safe_name}.md"
                
                files.append(GeneratedFile(
                    path=f"meetings/actions/{meeting_id}/{filename}",
                    content=doc_content,
                    file_type='documentation',
                    description=f"Action item documentation (line {action.line_number})",
                    source_line=action.line_number
                ))
        
        return files
    
    def generate_skill_gap_report(self, action_items: List[ActionItem],
                                  skill_links: Dict[int, SkillLinkResult],
                                  meeting_id: str) -> Optional[GeneratedFile]:
        """Generate a skill gap report if any items have skill gaps."""
        gaps = []
        
        for action in action_items:
            skill_link = skill_links.get(action.line_number)
            if skill_link and skill_link.has_skill_gap:
                gaps.append({
                    'action': action.raw_text,
                    'line': action.line_number,
                    'keywords': action.keywords
                })
        
        if not gaps:
            return None
        
        content = self._build_skill_gap_report(gaps, meeting_id)
        
        return GeneratedFile(
            path=f"meetings/reports/{meeting_id}-skill-gaps.md",
            content=content,
            file_type='documentation',
            description="Skill gap analysis report"
        )
    
    def _get_extension(self, language: Optional[str]) -> str:
        """Get file extension from language identifier."""
        ext_map = {
            'python': '.py', 'py': '.py',
            'javascript': '.js', 'js': '.js',
            'typescript': '.ts', 'ts': '.ts',
            'yaml': '.yaml', 'yml': '.yaml',
            'json': '.json',
            'bash': '.sh', 'sh': '.sh', 'shell': '.sh',
            'markdown': '.md', 'md': '.md',
            'html': '.html',
            'css': '.css',
            'sql': '.sql',
            'go': '.go',
            'rust': '.rs',
            'java': '.java'
        }
        
        if language:
            return ext_map.get(language.lower(), '.txt')
        return '.txt'
    
    def _generate_code_header(self, snippet: CodeSnippet, meeting_id: str) -> str:
        """Generate a header comment for code files."""
        language = snippet.language or 'unknown'
        
        comment_styles = {
            'py': '#', 'python': '#', 'sh': '#', 'bash': '#', 'yaml': '#', 'yml': '#',
            'js': '//', 'javascript': '//', 'ts': '//', 'typescript': '//',
            'java': '//', 'go': '//', 'rust': '//',
            'html': '<!--', 'css': '/*', 'sql': '--'
        }
        
        comment_prefix = comment_styles.get(language.lower(), '#')
        
        if comment_prefix == '<!--':
            return f"""<!-- 
Generated by Meeting-Code-Deployer
Source: {meeting_id}, Line {snippet.line_number}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-->"""
        elif comment_prefix == '/*':
            return f"""/* 
 * Generated by Meeting-Code-Deployer
 * Source: {meeting_id}, Line {snippet.line_number}
 * Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */"""
        else:
            return f"""{comment_prefix} Generated by Meeting-Code-Deployer
{comment_prefix} Source: {meeting_id}, Line {snippet.line_number}
{comment_prefix} Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _build_meeting_summary(self, action_items: List[ActionItem],
                               decisions: List[Decision],
                               skill_links: Dict[int, SkillLinkResult],
                               meeting_id: str,
                               meeting_date: str) -> str:
        """Build meeting summary markdown content."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""---
meeting_id: {meeting_id}
date: {meeting_date}
generated_at: {now}
generated_by: Meeting-Code-Deployer v2.0.0
---

# Meeting Summary: {meeting_id}

## Overview

| Metric | Count |
|--------|-------|
| Action Items | {len(action_items)} |
| Decisions | {len(decisions)} |
| Skill Links | {len([s for s in skill_links.values() if s and s.primary_skill])} |
| Skill Gaps | {len([s for s in skill_links.values() if s and s.has_skill_gap])} |

---

## Action Items

"""
        
        if action_items:
            for action in action_items:
                skill_link = skill_links.get(action.line_number)
                skill_info = ""
                if skill_link and skill_link.primary_skill:
                    skill_info = f" → [{skill_link.primary_skill.node_name}]({skill_link.primary_skill.node_path})"
                
                assignee = action.assignee or "Unassigned"
                deadline = action.deadline or "No deadline"
                
                content += f"""### Line {action.line_number}: {assignee.title()}

> {action.raw_text}

- **Assignee:** {assignee}
- **Deadline:** {deadline}
- **Confidence:** {action.confidence:.0%}
- **Skill Node:** {skill_info or 'None matched'}
- **Keywords:** {', '.join(action.keywords) if action.keywords else 'None'}

"""
        else:
            content += "*No action items extracted.*\n\n"
        
        content += "---\n\n## Decisions\n\n"
        
        if decisions:
            for decision in decisions:
                content += f"""### Line {decision.line_number}

> {decision.raw_text}

- **Speaker:** {decision.speaker or 'Unknown'}
- **Keywords:** {', '.join(decision.keywords) if decision.keywords else 'None'}

"""
        else:
            content += "*No decisions recorded.*\n\n"
        
        content += f"""---

## Next Steps

1. Review extracted action items
2. Assign tasks to appropriate agents
3. Link to skill-web nodes for context
4. Create task files in `tasks/backlog/`

---

*Auto-generated by Meeting-Code-Deployer*
"""
        
        return content
    
    def _build_action_doc(self, action: ActionItem, 
                          skill_link: Optional[SkillLinkResult],
                          meeting_id: str) -> str:
        """Build individual action item documentation."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        skill_section = ""
        if skill_link and skill_link.primary_skill:
            skill_section = f"""## Linked Skill Node

- **Primary:** [{skill_link.primary_skill.node_name}]({skill_link.primary_skill.node_path})
- **Domain:** {skill_link.primary_skill.domain}
- **Confidence:** {skill_link.primary_skill.confidence:.0%}
"""
            if skill_link.secondary_skills:
                skill_section += "\n### Secondary Skills\n\n"
                for sec in skill_link.secondary_skills:
                    skill_section += f"- [{sec.node_name}]({sec.node_path}) ({sec.confidence:.0%})\n"
        
        content = f"""---
source_meeting: {meeting_id}
line_number: {action.line_number}
assignee: {action.assignee or 'unassigned'}
deadline: {action.deadline or 'none'}
generated_at: {now}
---

# Action Item: Line {action.line_number}

## Original Statement

> {action.raw_text}

## Details

| Field | Value |
|-------|-------|
| Speaker | {action.speaker or 'Unknown'} |
| Assignee | {action.assignee or 'Unassigned'} |
| Deadline | {action.deadline or 'Not specified'} |
| Confidence | {action.confidence:.0%} |
| Keywords | {', '.join(action.keywords) if action.keywords else 'None'} |

{skill_section}

## Notes

*Add implementation notes here*

---

*Generated by Meeting-Code-Deployer*
"""
        
        return content
    
    def _build_skill_gap_report(self, gaps: List[Dict[str, Any]], 
                                meeting_id: str) -> str:
        """Build skill gap report."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""---
report_type: skill_gap_analysis
meeting_id: {meeting_id}
generated_at: {now}
gap_count: {len(gaps)}
---

# Skill Gap Report: {meeting_id}

## Summary

**{len(gaps)} action items** could not be confidently linked to existing skill-web nodes.

## Gaps Identified

"""
        
        for i, gap in enumerate(gaps, 1):
            content += f"""### Gap {i}: Line {gap['line']}

> {gap['action']}

**Keywords:** {', '.join(gap['keywords']) if gap['keywords'] else 'None identified'}

**Recommendation:** 
- Create new skill node OR
- Escalate to Chief (Grok) for assignment

"""
        
        content += f"""---

## Resolution Workflow

1. Review each gap above
2. Determine if new skill node needed
3. If yes, create in `_shared/skill-graphs/bprd-core/`
4. Assign task to agent with closest skill match
5. Update this report when resolved

---

*Auto-generated by Meeting-Code-Deployer*
"""
        
        return content
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        # Remove non-alphanumeric characters
        sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        # Replace spaces with hyphens
        sanitized = re.sub(r'\s+', '-', sanitized)
        # Remove multiple hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Lowercase and trim
        return sanitized.lower().strip('-')[:30]
