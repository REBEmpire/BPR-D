# Instructions

## CRITICAL CORRECTION (Claude Session 2026-02-19 18:30 UTC)

**PHANTOM FILE DISCOVERED:** api_healer.py does NOT exist in the repository.
Previous assessment of "deployment bottleneck" was incorrect - this is a creation bottleneck.

The infrastructure IS functional (15 sessions, 18 briefs, meetings working). API failures are real but not blocking all work. The healer will improve reliability, but it must be created first.

## Action Items

| Task | Assigned To | Priority | Status | Due |
|------|-------------|----------|--------|-----|
| Provide architectural guidance for api_healer.py design | Claude | URGENT | Pending | 2026-02-19 EOD |
| Implement pending_abacus_review flag | Claude | High | In Progress | 2026-02-20 |
| Audit 5 research briefs for quality | Claude | High | In Progress | 2026-02-20 |
| Document Infrastructure Resilience Learnings | Claude | High | In Progress | 2026-02-20 |
| Design Abacus Reintegration Framework | Claude | High | Pending | 2026-02-22 |

## Backlog

| Task | Assigned To | Priority | Status | Due |
|------|-------------|----------|--------|-----|
| Create Post-Crisis Deployment Checklist | Claude | High | Pending | 2026-02-21 |
| Design Meeting Quality Assessment Framework | Claude | Medium | Pending | 2026-02-23 |
| Review api_healer.py implementation (post-creation) | Claude | High | Pending | 2026-02-21 |

## Architectural Guidance for api_healer.py

**Design Principles:**
1. **Fail gracefully:** Never block operations, only improve reliability
2. **Observable:** Rich logging for pattern analysis
3. **Adaptive:** Learn from failures, adjust strategies
4. **Minimal dependencies:** Integrate cleanly with existing service

**Recommended Architecture:**
```python
class APIHealer:
    def __init__(self):
        self.model_cache = {}  # Cache working models
        self.failure_log = []  # Track patterns
        
    async def discover_models(self, provider: str):
        """Query provider API for available models"""
        
    async def heal_call(self, provider: str, model: str, **kwargs):
        """Wrap API call with retry + fallback logic"""
        
    def analyze_failures(self):
        """Generate insights from failure patterns"""
```

**Integration Points:**
- Wrap existing API calls in `heal_call()`
- Add `/api/healer/status` endpoint for monitoring
- Log to structured format for Abacus analysis

## Requests for Team
- Gemini: Implement healer with above architecture by Feb 20 EOD
- Grok: Adjust validation timeline for creation vs deployment
- Russell: Review healer design before Gemini implements
- Abacus: Timeline adjusted, all Feb 23 tasks remain valid