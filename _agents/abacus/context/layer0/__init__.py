"""Truth Sentinel - Layer 0 Semantic Validation

A validation layer for LLM responses that ensures semantic coherence,
detects contradictions, and flags potential hallucinations.

Example:
    from bprd_truth_sentinel import TruthSentinel, SentinelAction
    
    sentinel = TruthSentinel(coherence_threshold=0.7)
    result = sentinel.validate(llm_response)
    
    if result.action == SentinelAction.PASS:
        proceed_with_response(llm_response)
    elif result.action == SentinelAction.RE_QUERY:
        retry_llm_call()
    else:  # HUMAN_REVIEW
        flag_for_human_review(llm_response)
"""

from .truth_sentinel import (
    TruthSentinel,
    SentinelAction,
    ValidationResult,
    validate_response,
)

__version__ = "0.1.0"
__all__ = [
    "TruthSentinel",
    "SentinelAction", 
    "ValidationResult",
    "validate_response",
]
