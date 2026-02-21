# Truth Sentinel - Layer 0 Semantic Validation

A validation layer for LLM responses that ensures semantic coherence, detects contradictions, and flags potential hallucinations before they reach the Quality Gate.

## Philosophy

> **Truth is revealed through negation.**

The Truth Sentinel operates on the principle that defining failure conditions explicitly helps ensure valid responses. Rather than only checking what makes a response "good," we actively look for what makes it "bad":

- **Semantic incoherence** - Does the response make sense?
- **Internal contradictions** - Does it contradict itself?
- **Hallucination indicators** - Are there signs of fabrication?

## Installation

```bash
cd /home/ubuntu/bprd_truth_sentinel
pip install -r requirements.txt
```

## Quick Start

```python
from bprd_truth_sentinel import TruthSentinel, SentinelAction

# Initialize with default settings
sentinel = TruthSentinel(coherence_threshold=0.7)

# Validate a response
result = sentinel.validate(llm_response)

# Take action based on result
if result.action == SentinelAction.PASS:
    proceed_with_response(llm_response)
elif result.action == SentinelAction.RE_QUERY:
    retry_llm_call()
else:  # HUMAN_REVIEW
    flag_for_human_review(llm_response)
```

## Integration with API Healer

The Truth Sentinel is designed to work with the existing `heal_async()` pattern in `api_healer.py`:

```python
from bprd_truth_sentinel import TruthSentinel, SentinelAction
from api_healer import APIHealer

sentinel = TruthSentinel(
    config_path="_agents/abacus/context/layer0/negation_rubric.yaml",
    coherence_threshold=0.7,
    log_dir="_agents/_logs"
)
healer = APIHealer()

async def validated_api_call():
    # Step 1: Execute with API Healer
    result = await healer.heal_async(api_call_function, *args)
    
    # Step 2: Validate with Truth Sentinel
    validated_result, validation = await sentinel.wrap_healer_output(
        result,
        re_query_callback=lambda: healer.heal_async(api_call_function, *args),
        max_retries=2
    )
    
    # Step 3: Handle based on validation
    if validation.action == SentinelAction.PASS:
        return validated_result
    elif validation.action == SentinelAction.RE_QUERY:
        # Already retried, escalate to human
        return flag_for_review(validated_result, validation)
    else:
        return await human_review_queue.add(validated_result, validation)
```

### Pipeline Position

```
[Research Brief] → [Backlog Discovery] → [Daily Briefing] → 
[Content Generation] → [Image Sourcing] → 
[Staging & Review] ← Truth Sentinel intercepts here
    ↓
[API Healer] → [Truth Sentinel] → [Quality Gate (≥92)] → [Publishing]
```

## Configuration

### Using negation_rubric.yaml

```python
sentinel = TruthSentinel(
    config_path="path/to/negation_rubric.yaml",
    coherence_threshold=0.7,  # Override config value
    model_name="all-MiniLM-L6-v2",
    log_dir="_agents/_logs"
)
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `coherence_threshold` | 0.7 | Minimum score for PASS |
| `high_confidence_threshold` | 0.85 | Score for high-confidence PASS |
| `low_confidence_threshold` | 0.5 | Below triggers HUMAN_REVIEW |
| `model_name` | all-MiniLM-L6-v2 | Sentence transformer model |
| `log_dir` | _agents/_logs | JSON log output directory |

### Action Mappings

| Condition | Default Action |
|-----------|----------------|
| Score ≥ 0.85 | `PASS` |
| Score ≥ 0.70 | `PASS` |
| Score ≥ 0.50 | `RE_QUERY` |
| Score < 0.50 | `HUMAN_REVIEW` |
| Contradiction detected | `RE_QUERY` |
| Hallucination flagged | `HUMAN_REVIEW` |

## ValidationResult

```python
@dataclass
class ValidationResult:
    action: SentinelAction  # PASS, RE_QUERY, HUMAN_REVIEW
    coherence_score: float  # 0.0 to 1.0
    contradiction_detected: bool
    hallucination_indicators: List[str]
    timestamp: str
    reasoning: str
    metadata: Dict[str, Any]
```

## Hallucination Indicators

The Truth Sentinel detects these hallucination patterns:

| Indicator | Description |
|-----------|-------------|
| `empty_reasoning` | Empty or whitespace-only response |
| `vague_claims` | Excessive hedging (probably, maybe, might) |
| `missing_citations` | Claims sources without providing them |
| `repetitive_filler` | Repeated words indicating generation issues |
| `truncated_response` | Response appears cut off |
| `generic_filler` | AI-style filler language |

## Logging

Logs are written as JSON Lines to `_agents/_logs/truth_sentinel_{date}.json`:

```json
{
  "timestamp": "2026-02-20T10:30:00.000Z",
  "input_preview": "The generated content discusses...",
  "validation": {
    "action": "pass",
    "coherence_score": 0.87,
    "contradiction_detected": false,
    "hallucination_indicators": [],
    "reasoning": "Response passed all validation checks"
  }
}
```

## Handoff Templates

Updated handoff templates with the `negation_test` field are in `templates/`:

- `handoff.md` - Basic template
- `handoff-with-skill-links.md` - Extended template with YAML frontmatter

### The Negation Test Field

Every handoff must now include:

```markdown
## Negation Test

> **FAIL Condition:** [Describe the condition under which this task would FAIL silently]
```

Or in YAML frontmatter:

```yaml
negation_test: |
  Describe the condition under which this task would FAIL silently.
  Example: "FAIL if: Generated summary omits critical risk factors mentioned in source"
```

### Why Negation Tests?

The negation test forces explicit articulation of failure modes that:
1. Would not trigger obvious errors
2. Could pass automated quality checks
3. Would silently degrade output quality

Examples:
- "FAIL if: External API returns cached data older than 24 hours without indication"
- "FAIL if: Generated content passes spell-check but contains factual errors"
- "FAIL if: Image appears valid but has watermarks or licensing restrictions"

## Project Structure

```
bprd_truth_sentinel/
├── __init__.py              # Clean exports
├── truth_sentinel.py        # Main TruthSentinel class
├── negation_rubric.yaml     # Configuration
├── requirements.txt         # Dependencies
├── README.md               # This file
├── templates/
│   ├── handoff.md          # Basic handoff template
│   └── handoff-with-skill-links.md  # Extended template
└── tests/
    └── (test files)
```

## Example: Full Pipeline Integration

```python
import asyncio
from bprd_truth_sentinel import TruthSentinel, SentinelAction

async def content_pipeline(brief: str):
    """Content generation with Truth Sentinel validation."""
    
    sentinel = TruthSentinel(
        config_path="negation_rubric.yaml",
        coherence_threshold=0.7
    )
    
    # Generate content (via API Healer)
    content = await healer.heal_async(generate_content, brief)
    
    # Validate with Truth Sentinel
    validated, result = await sentinel.wrap_healer_output(
        content,
        reference=brief,  # Compare coherence to original brief
        re_query_callback=lambda: healer.heal_async(generate_content, brief),
        max_retries=2
    )
    
    # Log validation outcome
    print(f"Validation: {result.action.value}")
    print(f"Coherence: {result.coherence_score:.2f}")
    print(f"Reasoning: {result.reasoning}")
    
    # Route based on action
    if result.action == SentinelAction.PASS:
        # Proceed to Quality Gate
        return await quality_gate.grade(validated)
    elif result.action == SentinelAction.HUMAN_REVIEW:
        # Flag for human review
        return await review_queue.submit(validated, result)
    else:
        # Should not reach here after retries
        raise ValueError(f"Unexpected state: {result.action}")

# Run
asyncio.run(content_pipeline("Write about AI safety"))
```

## License

Internal BPR&D Project - REBEmpire
