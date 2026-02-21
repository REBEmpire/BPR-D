"""Integration module for Truth Sentinel.

Provides wrappers for integrating Truth Sentinel with existing
BPR&D infrastructure, particularly the API Healer in safe_llm_call.py.
"""

from .sentinel_wrapper import (
    SentinelWrapper,
    HealAndValidateResult,
    create_wrapper,
)

__all__ = [
    "SentinelWrapper",
    "HealAndValidateResult",
    "create_wrapper",
]
