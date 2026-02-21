"""Sentinel Wrapper - Integration layer for API Healer + Truth Sentinel.

This wrapper combines the API Healer's healing capabilities with the
Truth Sentinel's semantic validation. It's designed to be used in
safe_llm_call.py after healer.apply_healing(response).

Integration Point: crewai-service/tools/safe_llm_call.py
Position: After healer.apply_healing(), before returning response

Example usage in safe_llm_call.py:
    from integration.sentinel_wrapper import SentinelWrapper
    
    wrapper = SentinelWrapper(healer, sentinel)
    validated_response = await wrapper.heal_and_validate(response, retry_fn)
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple, Union

# Import Truth Sentinel components
try:
    from ..truth_sentinel import TruthSentinel, SentinelAction, ValidationResult
except ImportError:
    # Fallback for direct imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from truth_sentinel import TruthSentinel, SentinelAction, ValidationResult


@dataclass
class HealAndValidateResult:
    """Combined result from healer + sentinel validation."""
    response: Any
    healed: bool
    validation: ValidationResult
    retries_used: int
    final_action: SentinelAction
    
    @property
    def passed(self) -> bool:
        """True if response passed all validation."""
        return self.final_action == SentinelAction.PASS
    
    @property
    def needs_human_review(self) -> bool:
        """True if response requires human review."""
        return self.final_action == SentinelAction.HUMAN_REVIEW
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "healed": self.healed,
            "validation": self.validation.to_dict(),
            "retries_used": self.retries_used,
            "final_action": self.final_action.value,
            "passed": self.passed,
            "needs_human_review": self.needs_human_review
        }


class SentinelWrapper:
    """Wrapper that combines API Healer with Truth Sentinel validation.
    
    This class provides a unified interface for:
    1. Applying API Healer's healing to responses
    2. Running Truth Sentinel semantic validation
    3. Handling RE_QUERY actions with automatic retries
    4. Flagging HUMAN_REVIEW cases appropriately
    
    Designed for integration at safe_llm_call.py after healer.apply_healing().
    """
    
    def __init__(
        self,
        healer: Any = None,
        sentinel: Optional[TruthSentinel] = None,
        config_path: Optional[str] = None,
        coherence_threshold: float = 0.7,
        max_retries: int = 2,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Sentinel Wrapper.
        
        Args:
            healer: API Healer instance (optional, can be None if healing done externally)
            sentinel: TruthSentinel instance (created if not provided)
            config_path: Path to negation_rubric.yaml
            coherence_threshold: Minimum coherence score for PASS
            max_retries: Maximum RE_QUERY retry attempts
            logger: Optional logger instance
        """
        self.healer = healer
        self.sentinel = sentinel or TruthSentinel(
            config_path=config_path,
            coherence_threshold=coherence_threshold
        )
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)
    
    def _extract_text(self, response: Any) -> str:
        """Extract text content from various response formats."""
        if isinstance(response, str):
            return response
        elif hasattr(response, "content"):
            return response.content
        elif isinstance(response, dict):
            return response.get("content", response.get("text", str(response)))
        else:
            return str(response)
    
    async def heal_and_validate(
        self,
        response: Any,
        retry_callback: Optional[Callable] = None,
        reference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        apply_healing: bool = True
    ) -> HealAndValidateResult:
        """Apply healing and validation to a response.
        
        This is the main integration method. Call this after receiving
        an LLM response to:
        1. Apply API Healer healing (if healer provided and apply_healing=True)
        2. Run Truth Sentinel validation
        3. Handle RE_QUERY with retries
        4. Return combined result
        
        Args:
            response: The LLM response to process
            retry_callback: Async function to call for RE_QUERY retries
            reference: Optional reference text for coherence comparison
            context: Optional metadata about the request
            apply_healing: Whether to apply healer.apply_healing()
            
        Returns:
            HealAndValidateResult with response, validation, and action
        """
        current_response = response
        healed = False
        retries_used = 0
        
        # Step 1: Apply API Healer healing if available
        if apply_healing and self.healer is not None:
            try:
                if hasattr(self.healer, "apply_healing"):
                    current_response = self.healer.apply_healing(current_response)
                    healed = True
                elif hasattr(self.healer, "heal_async"):
                    current_response = await self.healer.heal_async(current_response)
                    healed = True
            except Exception as e:
                self.logger.warning(f"Healer apply_healing failed: {e}")
        
        # Step 2: Run Truth Sentinel validation
        response_text = self._extract_text(current_response)
        validation = await self.sentinel.validate_async(response_text, reference, context)
        
        # Step 3: Handle RE_QUERY with retries
        while validation.action == SentinelAction.RE_QUERY and retries_used < self.max_retries:
            if retry_callback is None:
                self.logger.warning("RE_QUERY action but no retry_callback provided")
                break
            
            retries_used += 1
            self.logger.info(f"RE_QUERY: Retry attempt {retries_used}/{self.max_retries}")
            
            try:
                # Get new response
                if asyncio.iscoroutinefunction(retry_callback):
                    current_response = await retry_callback()
                else:
                    current_response = retry_callback()
                
                # Apply healing to retry response
                if apply_healing and self.healer is not None:
                    try:
                        if hasattr(self.healer, "apply_healing"):
                            current_response = self.healer.apply_healing(current_response)
                    except Exception as e:
                        self.logger.warning(f"Healer apply_healing on retry failed: {e}")
                
                # Re-validate
                response_text = self._extract_text(current_response)
                validation = await self.sentinel.validate_async(
                    response_text, 
                    reference,
                    {**(context or {}), "retry_attempt": retries_used}
                )
                
            except Exception as e:
                self.logger.error(f"Retry callback failed: {e}")
                break
        
        # Step 4: Determine final action
        final_action = validation.action
        
        # If we exhausted retries on RE_QUERY, escalate to HUMAN_REVIEW
        if final_action == SentinelAction.RE_QUERY and retries_used >= self.max_retries:
            self.logger.warning("Max retries exhausted, escalating to HUMAN_REVIEW")
            final_action = SentinelAction.HUMAN_REVIEW
        
        return HealAndValidateResult(
            response=current_response,
            healed=healed,
            validation=validation,
            retries_used=retries_used,
            final_action=final_action
        )
    
    def validate_sync(
        self,
        response: Any,
        reference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Synchronous validation without healing or retries.
        
        Use this for simple validation cases where you just need
        to check a response without the full heal-and-retry flow.
        """
        response_text = self._extract_text(response)
        return self.sentinel.validate(response_text, reference, context)
    
    async def validate_async(
        self,
        response: Any,
        reference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Async validation without healing or retries."""
        response_text = self._extract_text(response)
        return await self.sentinel.validate_async(response_text, reference, context)


# Convenience function for quick integration
def create_wrapper(
    healer: Any = None,
    config_path: str = "_agents/abacus/context/layer0/negation_rubric.yaml",
    coherence_threshold: float = 0.7,
    max_retries: int = 2
) -> SentinelWrapper:
    """Create a SentinelWrapper with default settings.
    
    Example in safe_llm_call.py:
        from integration.sentinel_wrapper import create_wrapper
        
        wrapper = create_wrapper(healer=api_healer)
        
        async def safe_llm_call(prompt, **kwargs):
            response = await llm_client.generate(prompt, **kwargs)
            result = await wrapper.heal_and_validate(
                response,
                retry_callback=lambda: llm_client.generate(prompt, **kwargs)
            )
            
            if result.needs_human_review:
                await flag_for_review(result)
            
            return result.response
    """
    return SentinelWrapper(
        healer=healer,
        config_path=config_path,
        coherence_threshold=coherence_threshold,
        max_retries=max_retries
    )


# Export for integration
__all__ = [
    "SentinelWrapper",
    "HealAndValidateResult", 
    "create_wrapper",
    "SentinelAction",
    "ValidationResult"
]
