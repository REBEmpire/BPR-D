"""Task Creator - Creates properly formatted v2 tasks with IDs."""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from .parser import ActionItem
from .skill_linker import SkillLinkResult


@dataclass
class TaskFile:
    """Represents a task file to be created."""
    task_id: str
    path: str
    content: str
    title: str
    status: str = "Created"
    owner: Optional[str] = None
    skill_web_node: Optional[str] = None
    source: str = ""
    verification_criteria: List[str] = field(default_factory=list)


class TaskCreator:
    """Creates v2 task files following BPR&D conventions."""
    
    def __init__(self, config: Dict[str, Any], repo_root: str = "."):
        self.config = config
        self.repo_root = Path(repo_root)
        
        paths_config = config.get('mcd', {}).get('paths', {})
        self.tasks_dir = self.repo_root / paths_config.get('tasks_dir', 'tasks')
        self.counter_file = self.repo_root / paths_config.get('counter_file', 'tasks/_counter.yaml')
        self.todo_list_path = self.repo_root / paths_config.get('todo_list', 'BPR&D_To_Do_List.md')
    
    def get_next_task_id(self, dry_run: bool = False) -> str:
        """Get the next available task ID."""
        year = datetime.now().year
        
        # Try to read current counter
        if self.counter_file.exists():
            try:
                with open(self.counter_file, 'r') as f:
                    counter_data = yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError):
                counter_data = {}
        else:
            counter_data = {}
        
        # Get current counter for year
        year_key = str(year)
        current_count = counter_data.get(year_key, 4)  # Start after existing tasks (0004)
        next_count = current_count + 1
        
        # Update counter file (unless dry run)
        if not dry_run:
            counter_data[year_key] = next_count
            self.counter_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.counter_file, 'w') as f:
                yaml.dump(counter_data, f)
        
        # Format task ID
        return f"BPRD-{year}-{next_count:04d}"
    
    def peek_next_task_ids(self, count: int) -> List[str]:
        """Preview the next N task IDs without incrementing counter."""
        year = datetime.now().year
        
        if self.counter_file.exists():
            try:
                with open(self.counter_file, 'r') as f:
                    counter_data = yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError):
                counter_data = {}
        else:
            counter_data = {}
        
        current_count = counter_data.get(str(year), 4)
        
        return [f"BPRD-{year}-{current_count + i + 1:04d}" for i in range(count)]
    
    def create_task_from_action(self, action: ActionItem, 
                                skill_link: Optional[SkillLinkResult],
                                meeting_source: str,
                                task_id: Optional[str] = None,
                                dry_run: bool = False) -> TaskFile:
        """Create a task file from an action item."""
        if task_id is None:
            task_id = self.get_next_task_id(dry_run=dry_run)
        
        # Determine task directory based on status
        owner = action.assignee or (skill_link.suggested_owner if skill_link else None)
        status = "Assigned" if owner else "Created"
        
        if status == "Created":
            task_dir = self.tasks_dir / "backlog"
        else:
            task_dir = self.tasks_dir / "active"
        
        task_path = task_dir / f"{task_id}.md"
        
        # Extract title from action text
        title = self._extract_title(action.raw_text)
        
        # Determine skill web node
        skill_node = None
        if skill_link and skill_link.primary_skill:
            skill_node = skill_link.primary_skill.node_name
        
        # Generate verification criteria
        verification_criteria = self._generate_verification_criteria(action, skill_node)
        
        # Build task content
        content = self._build_task_content(
            task_id=task_id,
            title=title,
            action=action,
            skill_link=skill_link,
            meeting_source=meeting_source,
            status=status,
            owner=owner,
            verification_criteria=verification_criteria
        )
        
        return TaskFile(
            task_id=task_id,
            path=str(task_path.relative_to(self.repo_root)),
            content=content,
            title=title,
            status=status,
            owner=owner,
            skill_web_node=skill_node,
            source=meeting_source,
            verification_criteria=verification_criteria
        )
    
    def _extract_title(self, raw_text: str) -> str:
        """Extract a concise title from action text."""
        # Remove speaker prefix if present
        text = re.sub(r'^[\*]*[A-Za-z]+[\*]*:\s*', '', raw_text)
        
        # Remove common prefixes
        prefixes = ['TODO:', 'ACTION:', 'TASK:', '@\\w+\\s+will\\s+']
        for prefix in prefixes:
            text = re.sub(f'^{prefix}', '', text, flags=re.IGNORECASE)
        
        # Clean up and truncate
        text = text.strip()
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Truncate to reasonable length
        if len(text) > 80:
            text = text[:77] + '...'
        
        return text or "Extracted Task"
    
    def _generate_verification_criteria(self, action: ActionItem, 
                                        skill_node: Optional[str]) -> List[str]:
        """Generate verification criteria based on action type."""
        criteria = []
        
        # Keyword-based criteria
        keywords = action.keywords
        text_lower = action.raw_text.lower()
        
        if 'implement' in text_lower or 'create' in text_lower:
            criteria.append("Code implementation completed")
            criteria.append("Unit tests pass")
        
        if 'test' in keywords or 'testing' in text_lower:
            criteria.append("All tests written and passing")
            criteria.append("Test coverage meets minimum threshold")
        
        if 'documentation' in keywords or 'doc' in text_lower:
            criteria.append("Documentation updated")
            criteria.append("README reflects changes")
        
        if 'deploy' in keywords or 'deployment' in text_lower:
            criteria.append("Successfully deployed to target environment")
            criteria.append("Deployment verified working")
        
        if 'api' in keywords:
            criteria.append("API endpoints functional")
            criteria.append("API documentation updated")
        
        if 'review' in keywords or 'review' in text_lower:
            criteria.append("Code review completed")
            criteria.append("Review feedback addressed")
        
        # Default criteria if none generated
        if not criteria:
            criteria = [
                "Task requirements met",
                "Changes reviewed and approved",
                "No regressions introduced"
            ]
        
        return criteria
    
    def _build_task_content(self, task_id: str, title: str,
                           action: ActionItem, 
                           skill_link: Optional[SkillLinkResult],
                           meeting_source: str,
                           status: str, owner: Optional[str],
                           verification_criteria: List[str]) -> str:
        """Build the markdown content for a task file."""
        now = datetime.now()
        now_iso = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        date_str = now.strftime('%Y-%m-%d')
        
        # Build skill web node reference
        skill_node = "unassigned"
        skill_link_text = ""
        if skill_link and skill_link.primary_skill:
            skill_node = skill_link.primary_skill.node_name
            skill_link_text = f"\n## Linked Skill\n\n[{skill_node}](../../{skill_link.primary_skill.node_path})"
            
            if skill_link.secondary_skills:
                skill_link_text += "\n\n### Related Skills\n\n"
                for sec in skill_link.secondary_skills[:3]:
                    skill_link_text += f"- [{sec.node_name}](../../{sec.node_path})\n"
        
        # Build verification criteria section
        criteria_yaml = "\n".join([f'  - "{c}"' for c in verification_criteria])
        criteria_md = "\n".join([f"- [ ] {c}" for c in verification_criteria])
        
        # Deadline
        deadline = action.deadline or "TBD"
        
        content = f"""---
id: {task_id}
title: "{title}"
status: {status}
priority: Medium
owner: {owner or 'unassigned'}
source: {meeting_source}#L{action.line_number}
skill_web_node: {skill_node}
created_at: {now_iso}
updated_at: {now_iso}
due: {deadline}
extracted_from:
  meeting_source: "{meeting_source}"
  speaker: "{action.speaker or 'Unknown'}"
  line_number: {action.line_number}
  raw_statement: "{action.raw_text.replace('"', "'")}"
verification_criteria:
{criteria_yaml}
---

# {task_id}: {title}

## Original Context

> "{action.raw_text}"
> — {action.speaker or 'Meeting Participant'}, Line {action.line_number}

## Description

{self._generate_description(action)}

## Requirements

- **Assignee:** {owner or 'Unassigned'}
- **Deadline:** {deadline}
- **Confidence:** {action.confidence:.0%}
- **Keywords:** {', '.join(action.keywords) if action.keywords else 'None'}
{skill_link_text}

## Verification Criteria

{criteria_md}

## Progress

- [ ] Initial review complete
- [ ] Implementation started
- [ ] Tests written
- [ ] Ready for review

## Notes

*Add implementation notes here*

---

*Auto-generated by Meeting-Code-Deployer at {now.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return content
    
    def _generate_description(self, action: ActionItem) -> str:
        """Generate a description from action text."""
        text = action.raw_text
        
        # Try to extract core requirement
        patterns = [
            (r'implement\s+(.+)', 'Implement {}'),
            (r'create\s+(.+)', 'Create {}'),
            (r'update\s+(.+)', 'Update {}'),
            (r'add\s+(.+)', 'Add {}'),
            (r'fix\s+(.+)', 'Fix {}'),
            (r'review\s+(.+)', 'Review {}'),
        ]
        
        text_lower = text.lower()
        for pattern, template in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return template.format(match.group(1).strip().capitalize())
        
        return f"Task extracted from meeting: {text[:100]}..."
    
    def update_todo_list(self, tasks: List[TaskFile], dry_run: bool = False) -> str:
        """Update the BPR&D To-Do List with new tasks."""
        if not tasks:
            return "No tasks to add to To-Do List."
        
        # Read current to-do list
        if self.todo_list_path.exists():
            current_content = self.todo_list_path.read_text(encoding='utf-8')
        else:
            current_content = "# BPR&D To-Do List v2\n\n*Auto-generated*\n"
        
        # Build new entries to add
        new_entries = self._format_todo_entries(tasks)
        
        # Find the "Recently Completed" section and insert before it
        insert_marker = "## Recently Completed"
        if insert_marker in current_content:
            parts = current_content.split(insert_marker)
            new_section = f"""## Newly Added (Meeting Extraction)

| ID | Task | Owner | Status | Source | Added |
|----|------|-------|--------|--------|-------|
{new_entries}

---

"""
            updated_content = parts[0] + new_section + insert_marker + parts[1]
        else:
            # Append at end
            updated_content = current_content + f"""\n\n## Newly Added (Meeting Extraction)

| ID | Task | Owner | Status | Source | Added |
|----|------|-------|--------|--------|-------|
{new_entries}
"""
        
        if not dry_run:
            self.todo_list_path.write_text(updated_content, encoding='utf-8')
            return f"Added {len(tasks)} tasks to BPR&D To-Do List"
        else:
            return f"[DRY RUN] Would add {len(tasks)} tasks to BPR&D To-Do List"
    
    def _format_todo_entries(self, tasks: List[TaskFile]) -> str:
        """Format tasks as To-Do List table entries."""
        entries = []
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        for task in tasks:
            # Truncate title for table display
            title = task.title[:40] + '...' if len(task.title) > 40 else task.title
            
            entry = f"| [{task.task_id}]({task.path}) | {title} | {task.owner or '-'} | {task.status} | Meeting | {date_str} |"
            entries.append(entry)
        
        return '\n'.join(entries)
    
    def write_tasks(self, tasks: List[TaskFile], dry_run: bool = False) -> Dict[str, Any]:
        """Write all task files to disk."""
        results = {
            'written': [],
            'skipped': [],
            'errors': []
        }
        
        for task in tasks:
            task_path = self.repo_root / task.path
            
            try:
                if dry_run:
                    results['skipped'].append({
                        'task_id': task.task_id,
                        'path': task.path,
                        'reason': 'dry_run'
                    })
                else:
                    # Ensure directory exists
                    task_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    task_path.write_text(task.content, encoding='utf-8')
                    
                    results['written'].append({
                        'task_id': task.task_id,
                        'path': task.path,
                        'title': task.title
                    })
            except Exception as e:
                results['errors'].append({
                    'task_id': task.task_id,
                    'path': task.path,
                    'error': str(e)
                })
        
        return results
