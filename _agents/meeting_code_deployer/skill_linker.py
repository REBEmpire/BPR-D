"""Skill Linker - Links extracted items to skill-web nodes."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import yaml


@dataclass
class SkillMatch:
    """Represents a skill-web node match."""
    node_name: str
    node_path: str
    confidence: float
    matched_keywords: List[str]
    domain: Optional[str] = None
    tier: Optional[str] = None


@dataclass
class SkillLinkResult:
    """Result of skill linking for an action item."""
    primary_skill: Optional[SkillMatch]
    secondary_skills: List[SkillMatch]
    has_skill_gap: bool
    suggested_owner: Optional[str] = None


class SkillLinker:
    """Links action items to skill-web nodes in the BPR&D knowledge graph."""
    
    def __init__(self, config: Dict[str, Any], repo_root: str = "."):
        self.config = config
        self.repo_root = Path(repo_root)
        self.skill_web_path = self.repo_root / config.get('mcd', {}).get('paths', {}).get(
            'skill_web', '_shared/skill-graphs/bprd-core'
        )
        
        # Load agents and their skills
        self.agents = {}
        for agent in config.get('mcd', {}).get('agents', []):
            self.agents[agent['name']] = agent.get('skills', [])
        
        # Build skill node index
        self.skill_nodes = self._build_skill_index()
        
        # Keyword to skill mapping
        self.keyword_skill_map = self._build_keyword_map()
    
    def _build_skill_index(self) -> Dict[str, Dict[str, Any]]:
        """Build an index of all skill nodes from the skill-web."""
        skill_nodes = {}
        
        if not self.skill_web_path.exists():
            return skill_nodes
        
        # Find all skill files
        for skill_file in self.skill_web_path.glob('*.md'):
            node_name = skill_file.stem
            content = skill_file.read_text(encoding='utf-8')
            
            # Extract metadata from YAML frontmatter
            metadata = self._extract_yaml_metadata(content)
            
            # Extract keywords from content
            keywords = self._extract_skill_keywords(content, node_name)
            
            skill_nodes[node_name] = {
                'path': str(skill_file.relative_to(self.repo_root)),
                'domain': metadata.get('domain', self._infer_domain(node_name)),
                'tier': metadata.get('tier', 'Core'),
                'keywords': keywords,
                'content': content
            }
        
        # Also check agent-hooks subdirectory
        hooks_path = self.skill_web_path / 'agent-hooks'
        if hooks_path.exists():
            for hook_file in hooks_path.glob('*.md'):
                node_name = hook_file.stem
                content = hook_file.read_text(encoding='utf-8')
                metadata = self._extract_yaml_metadata(content)
                keywords = self._extract_skill_keywords(content, node_name)
                
                skill_nodes[node_name] = {
                    'path': str(hook_file.relative_to(self.repo_root)),
                    'domain': 'Agent Hooks',
                    'tier': 'Core',
                    'keywords': keywords,
                    'content': content
                }
        
        return skill_nodes
    
    def _extract_yaml_metadata(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter metadata."""
        yaml_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
        if yaml_match:
            try:
                return yaml.safe_load(yaml_match.group(1)) or {}
            except yaml.YAMLError:
                pass
        return {}
    
    def _extract_skill_keywords(self, content: str, node_name: str) -> List[str]:
        """Extract keywords from skill node content."""
        keywords = []
        
        # Add keywords from node name
        name_parts = node_name.replace('skill-', '').replace('-', ' ').split()
        keywords.extend(name_parts)
        
        # Look for common technical terms in content
        tech_terms = [
            'api', 'database', 'frontend', 'backend', 'test', 'deploy', 'docker',
            'github', 'automation', 'pipeline', 'documentation', 'security',
            'meeting', 'handoff', 'research', 'content', 'memory', 'session',
            'telegram', 'alerts', 'monitoring', 'infrastructure', 'cost',
            'cognition', 'agent', 'prompt', 'backlog', 'discovery', 'wiki'
        ]
        
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower and term not in keywords:
                keywords.append(term)
        
        return keywords
    
    def _infer_domain(self, node_name: str) -> str:
        """Infer domain from node name."""
        domain_patterns = {
            'Orchestration': ['meeting', 'session', 'rotation', 'schedule', 'initiative'],
            'Backlog & Discovery': ['backlog', 'handoff', 'discovery', 'wiki'],
            'Agent Cognition': ['cognition', 'prompt', 'evolution', 'agent'],
            'Knowledge & Memory': ['memory', 'yaml', 'session', 'output'],
            'GitHub & Automation': ['github', 'commit', 'automation', 'hive', 'pipeline'],
            'Infrastructure': ['cost', 'render', 'telegram', 'deployment'],
            'Research Pipelines': ['research', 'content', 'image', 'quality', 'brief'],
            'Navigation': ['moc', 'graph', 'navigation', 'index']
        }
        
        name_lower = node_name.lower()
        for domain, patterns in domain_patterns.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return domain
        
        return 'General'
    
    def _build_keyword_map(self) -> Dict[str, List[str]]:
        """Build a reverse mapping from keywords to skill nodes."""
        keyword_map = {}
        
        for node_name, node_info in self.skill_nodes.items():
            for keyword in node_info['keywords']:
                if keyword not in keyword_map:
                    keyword_map[keyword] = []
                keyword_map[keyword].append(node_name)
        
        return keyword_map
    
    def link_action_item(self, action_text: str, keywords: List[str]) -> SkillLinkResult:
        """Link an action item to skill-web nodes."""
        matches = []
        
        # Score each skill node
        for node_name, node_info in self.skill_nodes.items():
            score, matched_keywords = self._calculate_match_score(
                action_text, keywords, node_info
            )
            
            if score > 0.1:  # Minimum threshold
                matches.append(SkillMatch(
                    node_name=node_name,
                    node_path=node_info['path'],
                    confidence=score,
                    matched_keywords=matched_keywords,
                    domain=node_info['domain'],
                    tier=node_info['tier']
                ))
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        # Determine primary and secondary skills
        primary_skill = matches[0] if matches else None
        secondary_skills = matches[1:4] if len(matches) > 1 else []
        
        # Check for skill gap
        has_skill_gap = primary_skill is None or primary_skill.confidence < 0.3
        
        # Suggest owner based on skill match
        suggested_owner = self._suggest_owner(action_text, primary_skill)
        
        return SkillLinkResult(
            primary_skill=primary_skill,
            secondary_skills=secondary_skills,
            has_skill_gap=has_skill_gap,
            suggested_owner=suggested_owner
        )
    
    def _calculate_match_score(self, action_text: str, keywords: List[str],
                               node_info: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate match score between action and skill node."""
        score = 0.0
        matched_keywords = []
        
        action_lower = action_text.lower()
        node_keywords = node_info['keywords']
        
        # Direct keyword matches
        for keyword in keywords:
            if keyword.lower() in node_keywords:
                score += 0.2
                matched_keywords.append(keyword)
        
        # Check if action text contains node keywords
        for node_keyword in node_keywords:
            if node_keyword in action_lower:
                score += 0.15
                if node_keyword not in matched_keywords:
                    matched_keywords.append(node_keyword)
        
        # Domain-specific boosts
        domain_keywords = {
            'GitHub & Automation': ['commit', 'push', 'pr', 'branch', 'merge', 'github'],
            'Infrastructure': ['deploy', 'server', 'render', 'telegram', 'alert'],
            'Research Pipelines': ['research', 'brief', 'content', 'hive', 'post'],
            'Orchestration': ['meeting', 'session', 'schedule', 'rotation'],
            'Backlog & Discovery': ['backlog', 'handoff', 'task', 'priority']
        }
        
        domain = node_info['domain']
        if domain in domain_keywords:
            for dk in domain_keywords[domain]:
                if dk in action_lower:
                    score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0), matched_keywords
    
    def _suggest_owner(self, action_text: str, primary_skill: Optional[SkillMatch]) -> Optional[str]:
        """Suggest an owner based on skill requirements."""
        if not primary_skill:
            return None
        
        # Build skill-to-agent map
        skill_domain_map = {
            'GitHub & Automation': ['abacus', 'claude'],
            'Infrastructure': ['abacus', 'russell'],
            'Research Pipelines': ['gemini', 'claude'],
            'Orchestration': ['grok', 'abacus'],
            'Backlog & Discovery': ['grok', 'abacus'],
            'Agent Cognition': ['claude', 'grok'],
            'Knowledge & Memory': ['claude', 'gemini'],
            'Navigation': ['claude', 'abacus']
        }
        
        domain = primary_skill.domain
        if domain in skill_domain_map:
            # Return first available agent for domain
            return skill_domain_map[domain][0]
        
        # Default to grok for strategic/unknown tasks
        return 'grok'
    
    def get_skill_node_path(self, node_name: str) -> Optional[str]:
        """Get the relative path to a skill node."""
        if node_name in self.skill_nodes:
            return self.skill_nodes[node_name]['path']
        return None
    
    def list_all_skills(self) -> List[str]:
        """List all available skill node names."""
        return list(self.skill_nodes.keys())
    
    def get_skill_by_domain(self, domain: str) -> List[str]:
        """Get all skill nodes for a domain."""
        return [
            name for name, info in self.skill_nodes.items()
            if info['domain'] == domain
        ]
