"""Truth Sentinel - Layer 0 semantic validation for LLM responses.

Integrates with the API Healer to validate semantic coherence,
detect contradictions, and flag potential hallucinations before
passing responses to the Quality Gate.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SentinelAction(Enum):
    """Actions the Truth Sentinel can take based on validation results."""
    PASS = "pass"
    RE_QUERY = "re_query"
    HUMAN_REVIEW = "human_review"


@dataclass
class ValidationResult:
    """Result of a Truth Sentinel validation."""
    action: SentinelAction
    coherence_score: float
    contradiction_detected: bool
    hallucination_indicators: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "coherence_score": self.coherence_score,
            "contradiction_detected": self.contradiction_detected,
            "hallucination_indicators": self.hallucination_indicators,
            "timestamp": self.timestamp,
            "reasoning": self.reasoning,
            "metadata": self.metadata
        }


class TruthSentinel:
    """Validates LLM responses for semantic coherence and factual consistency.
    
    The Truth Sentinel applies Layer 0 validation to catch:
    - Semantic incoherence (response doesn't make sense)
    - Internal contradictions (response contradicts itself)
    - Hallucination indicators (vague claims, missing citations, empty reasoning)
    
    Philosophy: Truth is revealed through negation. We detect failure conditions
    to ensure what passes is more likely to be valid.
    """
    
    DEFAULT_CONFIG = {
        "coherence_threshold": 0.7,
        "high_confidence_threshold": 0.85,
        "low_confidence_threshold": 0.5,
        "contradiction_patterns": [
            r"(?i)\b(however|but|although)\b.*\b(not|never|no)\b.*\b(same|similar|identical)\b",
            r"(?i)\b(is|are|was|were)\b.*\b(is not|are not|isn't|aren't)\b",
            r"(?i)\b(always|never)\b.*\b(sometimes|occasionally|rarely)\b",
            r"(?i)\b(true|correct)\b.*\b(false|incorrect|wrong)\b.*same",
        ],
        "hallucination_indicators": [
            {"name": "empty_reasoning", "pattern": r"^\s*$", "description": "Empty or whitespace-only response"},
            {"name": "vague_claims", "patterns": [r"(?i)\b(probably|maybe|might|could be|possibly)\b"], "threshold": 3},
            {"name": "missing_citations", "trigger_phrases": ["according to", "research shows", "studies indicate", "experts say"], "citation_pattern": r"\[\d+\]|\(\d{4}\)|https?://"},
            {"name": "repetitive_filler", "pattern": r"(\b\w+\b)(?:\s+\1){2,}", "description": "Repeated words indicating generation issues"},
            {"name": "truncated_response", "patterns": [r"\.\.\.$", r"(?<!\.)$"], "min_length": 50}
        ],
        "action_mappings": {
            "high_confidence": "pass",
            "medium_confidence": "pass",
            "low_confidence": "re_query",
            "very_low_confidence": "human_review",
            "contradiction_detected": "re_query",
            "hallucination_flagged": "human_review"
        }
    }
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        coherence_threshold: float = 0.7,
        model_name: str = "all-MiniLM-L6-v2",
        log_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Truth Sentinel.
        
        Args:
            config_path: Path to negation_rubric.yaml config file
            coherence_threshold: Minimum coherence score for PASS (0.0-1.0)
            model_name: Sentence transformer model for semantic scoring
            log_dir: Directory for JSON logs (default: _agents/_logs/)
            logger: Optional logger instance
        """
        self.config = self._load_config(config_path)
        self.coherence_threshold = coherence_threshold or self.config.get("coherence_threshold", 0.7)
        self.model_name = model_name
        self._model = None
        
        # Setup logging
        self.logger = logger or logging.getLogger(__name__)
        self.log_dir = Path(log_dir) if log_dir else Path("_agents/_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return self.DEFAULT_CONFIG.copy()
    
    @property
    def model(self):
        """Lazy-load the sentence transformer model."""
        if self._model is None:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers is required for semantic scoring. "
                    "Install with: pip install sentence-transformers"
                )
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def compute_coherence_score(self, text: str, reference: Optional[str] = None) -> float:
        """Compute semantic coherence score for a text.
        
        If reference is provided, scores similarity to reference.
        Otherwise, scores internal coherence by comparing sentence pairs.
        
        Args:
            text: The text to score
            reference: Optional reference text for comparison
            
        Returns:
            Coherence score between 0.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0
            
        if reference:
            # Compare to reference text
            embeddings = self.model.encode([text, reference], convert_to_tensor=True)
            similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
            return max(0.0, min(1.0, similarity))
        
        # Internal coherence: compare consecutive sentences
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            return 0.8  # Single sentence, assume moderate coherence
        
        embeddings = self.model.encode(sentences, convert_to_tensor=True)
        scores = []
        for i in range(len(embeddings) - 1):
            sim = util.cos_sim(embeddings[i], embeddings[i + 1]).item()
            scores.append(sim)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def detect_contradictions(self, text: str) -> Tuple[bool, List[str]]:
        """Detect internal contradictions in text.
        
        Returns:
            Tuple of (contradiction_found, list of matched patterns)
        """
        patterns = self.config.get("contradiction_patterns", self.DEFAULT_CONFIG["contradiction_patterns"])
        matches = []
        
        for pattern in patterns:
            if re.search(pattern, text):
                matches.append(pattern)
        
        # Also check for semantic contradictions between sentences
        sentences = self._split_sentences(text)
        if len(sentences) >= 2 and SENTENCE_TRANSFORMERS_AVAILABLE:
            # Check for negation patterns between related sentences
            for i, sent in enumerate(sentences):
                for j, other in enumerate(sentences[i+1:], i+1):
                    if self._sentences_contradict(sent, other):
                        matches.append(f"semantic_contradiction: '{sent[:50]}...' vs '{other[:50]}...'")
        
        return len(matches) > 0, matches
    
    def _sentences_contradict(self, sent1: str, sent2: str) -> bool:
        """Check if two sentences semantically contradict each other."""
        # Simple negation check
        negation_words = {"not", "never", "no", "none", "neither", "nobody", "nothing", "nowhere"}
        
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        # Check if same subject with opposite polarity
        common = words1 & words2 - {"the", "a", "an", "is", "are", "was", "were"}
        if len(common) > 2:  # Significant overlap
            neg1 = bool(words1 & negation_words)
            neg2 = bool(words2 & negation_words)
            if neg1 != neg2:  # One negated, one not
                return True
        
        return False
    
    def detect_hallucination_indicators(self, text: str) -> List[str]:
        """Detect indicators of potential hallucination.
        
        Returns:
            List of hallucination indicator names found
        """
        indicators = []
        config_indicators = self.config.get("hallucination_indicators", self.DEFAULT_CONFIG["hallucination_indicators"])
        
        for indicator in config_indicators:
            name = indicator["name"]
            
            if name == "empty_reasoning":
                if not text or not text.strip():
                    indicators.append(name)
                    
            elif name == "vague_claims":
                patterns = indicator.get("patterns", [])
                threshold = indicator.get("threshold", 3)
                count = sum(len(re.findall(p, text)) for p in patterns)
                if count >= threshold:
                    indicators.append(f"{name} (count: {count})")
                    
            elif name == "missing_citations":
                trigger_phrases = indicator.get("trigger_phrases", [])
                citation_pattern = indicator.get("citation_pattern", "")
                has_trigger = any(phrase.lower() in text.lower() for phrase in trigger_phrases)
                has_citation = bool(re.search(citation_pattern, text))
                if has_trigger and not has_citation:
                    indicators.append(name)
                    
            elif name == "repetitive_filler":
                pattern = indicator.get("pattern", "")
                if re.search(pattern, text):
                    indicators.append(name)
                    
            elif name == "truncated_response":
                min_length = indicator.get("min_length", 50)
                patterns = indicator.get("patterns", [])
                if len(text) >= min_length:
                    for p in patterns:
                        if re.search(p, text):
                            indicators.append(name)
                            break
        
        return indicators
    
    def determine_action(self, coherence_score: float, contradiction_detected: bool, 
                         hallucination_indicators: List[str]) -> SentinelAction:
        """Determine the appropriate action based on validation results."""
        mappings = self.config.get("action_mappings", self.DEFAULT_CONFIG["action_mappings"])
        high_threshold = self.config.get("high_confidence_threshold", 0.85)
        low_threshold = self.config.get("low_confidence_threshold", 0.5)
        
        # Priority: contradiction > hallucination > coherence
        if contradiction_detected:
            action_str = mappings.get("contradiction_detected", "re_query")
            return SentinelAction(action_str)
        
        if hallucination_indicators:
            action_str = mappings.get("hallucination_flagged", "human_review")
            return SentinelAction(action_str)
        
        if coherence_score >= high_threshold:
            action_str = mappings.get("high_confidence", "pass")
        elif coherence_score >= self.coherence_threshold:
            action_str = mappings.get("medium_confidence", "pass")
        elif coherence_score >= low_threshold:
            action_str = mappings.get("low_confidence", "re_query")
        else:
            action_str = mappings.get("very_low_confidence", "human_review")
        
        return SentinelAction(action_str)
    
    def validate(self, response: str, reference: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate an LLM response synchronously.
        
        Args:
            response: The LLM response to validate
            reference: Optional reference text for comparison
            context: Optional metadata about the request
            
        Returns:
            ValidationResult with action and scores
        """
        coherence_score = self.compute_coherence_score(response, reference)
        contradiction_detected, contradiction_matches = self.detect_contradictions(response)
        hallucination_indicators = self.detect_hallucination_indicators(response)
        
        action = self.determine_action(coherence_score, contradiction_detected, hallucination_indicators)
        
        reasoning_parts = []
        if coherence_score < self.coherence_threshold:
            reasoning_parts.append(f"Low coherence: {coherence_score:.2f} < {self.coherence_threshold}")
        if contradiction_detected:
            reasoning_parts.append(f"Contradictions found: {contradiction_matches}")
        if hallucination_indicators:
            reasoning_parts.append(f"Hallucination indicators: {hallucination_indicators}")
        if not reasoning_parts:
            reasoning_parts.append("Response passed all validation checks")
        
        result = ValidationResult(
            action=action,
            coherence_score=coherence_score,
            contradiction_detected=contradiction_detected,
            hallucination_indicators=hallucination_indicators,
            reasoning="; ".join(reasoning_parts),
            metadata=context or {}
        )
        
        self._log_result(response, result)
        return result
    
    async def validate_async(self, response: str, reference: Optional[str] = None,
                             context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate an LLM response asynchronously.
        
        Compatible with the heal_async() pattern in api_healer.py.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.validate, response, reference, context)
    
    def _log_result(self, input_text: str, result: ValidationResult) -> None:
        """Log validation result to JSON file."""
        log_file = self.log_dir / f"truth_sentinel_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        log_entry = {
            "timestamp": result.timestamp,
            "input_preview": input_text[:200] + "..." if len(input_text) > 200 else input_text,
            "validation": result.to_dict()
        }
        
        try:
            # Append to JSON lines file
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.warning(f"Failed to write log: {e}")
    
    async def wrap_healer_output(
        self,
        healer_result: Any,
        reference: Optional[str] = None,
        re_query_callback: Optional[Callable] = None,
        max_retries: int = 2
    ) -> Tuple[Any, ValidationResult]:
        """Wrap heal_async() output with Truth Sentinel validation.
        
        Example integration:
            sentinel = TruthSentinel()
            result = await healer.heal_async(api_call, *args)
            validated_result, validation = await sentinel.wrap_healer_output(
                result, 
                re_query_callback=lambda: healer.heal_async(api_call, *args)
            )
        
        Args:
            healer_result: The result from heal_async()
            reference: Optional reference for coherence comparison
            re_query_callback: Async function to retry if RE_QUERY action
            max_retries: Maximum re-query attempts
            
        Returns:
            Tuple of (final_result, ValidationResult)
        """
        # Extract text from result (handle different formats)
        if isinstance(healer_result, str):
            response_text = healer_result
        elif hasattr(healer_result, "content"):
            response_text = healer_result.content
        elif isinstance(healer_result, dict) and "content" in healer_result:
            response_text = healer_result["content"]
        else:
            response_text = str(healer_result)
        
        validation = await self.validate_async(response_text, reference)
        
        # Handle RE_QUERY action with retries
        retries = 0
        current_result = healer_result
        
        while validation.action == SentinelAction.RE_QUERY and retries < max_retries:
            if re_query_callback is None:
                self.logger.warning("RE_QUERY action but no callback provided")
                break
            
            self.logger.info(f"Re-querying (attempt {retries + 1}/{max_retries})")
            retries += 1
            
            current_result = await re_query_callback()
            if isinstance(current_result, str):
                response_text = current_result
            elif hasattr(current_result, "content"):
                response_text = current_result.content
            else:
                response_text = str(current_result)
            
            validation = await self.validate_async(
                response_text, 
                reference,
                {"retry_attempt": retries}
            )
        
        return current_result, validation


# Convenience function for quick validation
def validate_response(response: str, threshold: float = 0.7) -> ValidationResult:
    """Quick validation of a response with default settings."""
    sentinel = TruthSentinel(coherence_threshold=threshold)
    return sentinel.validate(response)
