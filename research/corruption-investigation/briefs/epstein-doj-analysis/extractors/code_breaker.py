"""
Code and alias detection for decoding communications.

Investigation Goal #1: Break Their Code

Identifies and decodes:
- Aliases and nicknames
- Code words and euphemisms
- Initials and abbreviations
- Suspicious patterns in correspondence
- Context-based term resolution

Builds a code dictionary mapping suspicious terms to likely meanings.
"""
import re
import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)


class CodeBreaker:
    """
    Detect and decode aliases, code words, and euphemisms.

    Strategies:
    1. Pattern recognition (quotes, capitalization, context)
    2. Initials expansion (cross-document correlation)
    3. Euphemism detection (suspicious phrasing)
    4. Alias resolution (entity co-occurrence)
    """

    # Known aliases from public records
    KNOWN_ALIASES = {
        'JE': 'Jeffrey Epstein',
        'GM': 'Ghislaine Maxwell',
        'GMax': 'Ghislaine Maxwell',
        'PA': 'Prince Andrew',
        'BC': 'Bill Clinton',
        'DJT': 'Donald Trump',
        'AD': 'Alan Dershowitz',
        'SK': 'Sarah Kellen',
        'NM': 'Nadia Marcinkova',
    }

    # Suspicious patterns that may indicate code words
    CODE_PATTERNS = [
        # Quoted unusual terms
        (r'"([^"]{3,20})"', 'quoted_term'),

        # ALL CAPS short words (potential code)
        (r'\b([A-Z]{2,6})\b', 'caps_term'),

        # Initials (2-3 capital letters)
        (r'\b([A-Z]\.?){2,3}\b', 'initials'),

        # Unusual spacing or characters
        (r'\b\w+[-_]\w+\b', 'hyphenated_term'),
    ]

    # Euphemism trigger words (context indicators)
    EUPHEMISM_TRIGGERS = [
        'massage', 'modeling', 'recruitment', 'referral',
        'entertainment', 'guest', 'assistant', 'friend',
        'introduction', 'meeting', 'appointment', 'session',
    ]

    # Suspicious context patterns
    SUSPICIOUS_CONTEXTS = [
        r'bring.*girl',
        r'young.*woman',
        r'introduce.*to',
        r'arrange.*meeting',
        r'private.*session',
        r'special.*guest',
    ]

    def __init__(self):
        """Initialize code breaker."""
        self.code_dictionary = {}  # Maps term -> likely meaning
        logger.info("CodeBreaker initialized")

    def detect_code_terms(
        self,
        text: str,
        entities: Dict,
        doc_id: str = None
    ) -> Dict:
        """
        Detect potential code words and aliases in text.

        Args:
            text: Document text
            entities: Extracted entities (for context)
            doc_id: Document identifier

        Returns:
            Dictionary of detected code terms:
            {
                'code_terms': [
                    {
                        'term': 'massage',
                        'likely_refers_to': 'sexual abuse (euphemism)',
                        'confidence_score': 0.75,
                        'pattern_type': 'euphemism',
                        'context_snippets': ['...provide massage to guests...'],
                        'occurrences': 5,
                    },
                    ...
                ],
                'aliases': [...],
                'initials': [...],
            }
        """
        logger.info(f"Detecting code terms in {doc_id or 'document'}")

        code_terms = []
        aliases = []
        initials = []

        # 1. Detect known aliases
        for alias, full_name in self.KNOWN_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', text):
                occurrences = len(re.findall(r'\b' + re.escape(alias) + r'\b', text))

                aliases.append({
                    'term': alias,
                    'likely_refers_to': full_name,
                    'confidence_score': 0.95,
                    'pattern_type': 'known_alias',
                    'context_snippets': self._extract_contexts(text, alias, max_contexts=3),
                    'occurrences': occurrences,
                })

        # 2. Detect euphemisms
        euphemisms = self._detect_euphemisms(text)
        code_terms.extend(euphemisms)

        # 3. Detect pattern-based code words
        pattern_codes = self._detect_pattern_codes(text)
        code_terms.extend(pattern_codes)

        # 4. Detect initials (unknown)
        unknown_initials = self._detect_unknown_initials(text, entities)
        initials.extend(unknown_initials)

        # 5. Detect suspicious quoted terms
        quoted_terms = self._detect_quoted_terms(text)
        code_terms.extend(quoted_terms)

        logger.info(
            f"Detected {len(code_terms)} code terms, "
            f"{len(aliases)} aliases, "
            f"{len(initials)} initials"
        )

        return {
            'code_terms': code_terms,
            'aliases': aliases,
            'initials': initials,
            'detection_metadata': {
                'total_detections': len(code_terms) + len(aliases) + len(initials),
                'source_doc': doc_id,
            }
        }

    def _detect_euphemisms(self, text: str) -> List[Dict]:
        """
        Detect potential euphemisms in text.

        Args:
            text: Document text

        Returns:
            List of detected euphemisms
        """
        euphemisms = []
        text_lower = text.lower()

        for trigger in self.EUPHEMISM_TRIGGERS:
            # Find all occurrences with context
            pattern = r'\b' + re.escape(trigger) + r'\b'
            matches = list(re.finditer(pattern, text_lower))

            if matches:
                contexts = self._extract_contexts(text, trigger, max_contexts=3)

                # Check if used in suspicious context
                suspicious_score = 0.0
                for suspicious_pattern in self.SUSPICIOUS_CONTEXTS:
                    if any(re.search(suspicious_pattern, ctx.lower()) for ctx in contexts):
                        suspicious_score += 0.3

                # Base confidence for known triggers
                confidence = 0.5 + suspicious_score

                # Only report if confidence meets threshold
                if confidence >= 0.6:
                    euphemisms.append({
                        'term': trigger,
                        'likely_refers_to': self._infer_euphemism_meaning(trigger, contexts),
                        'confidence_score': round(min(confidence, 0.95), 2),
                        'pattern_type': 'euphemism',
                        'context_snippets': contexts,
                        'occurrences': len(matches),
                    })

        return euphemisms

    def _detect_pattern_codes(self, text: str) -> List[Dict]:
        """
        Detect code words based on patterns (caps, spacing, etc.).

        Args:
            text: Document text

        Returns:
            List of detected pattern-based codes
        """
        codes = []

        for pattern, pattern_type in self.CODE_PATTERNS:
            matches = re.finditer(pattern, text)

            # Count occurrences
            term_counts = Counter()
            for match in matches:
                term = match.group(0) if match.lastindex is None else match.group(1)
                term_counts[term] += 1

            # Report terms with multiple occurrences
            for term, count in term_counts.items():
                # Skip common words
                if len(term) <= 2 or term.lower() in {'the', 'and', 'for', 'are', 'was'}:
                    continue

                # Skip if it's a known entity
                # (Would be enhanced with entity check)

                if count >= 2:  # At least 2 occurrences
                    confidence = min(0.5 + (count * 0.05), 0.85)

                    codes.append({
                        'term': term,
                        'likely_refers_to': 'unknown (requires investigation)',
                        'confidence_score': round(confidence, 2),
                        'pattern_type': pattern_type,
                        'context_snippets': self._extract_contexts(text, term, max_contexts=2),
                        'occurrences': count,
                    })

        return codes

    def _detect_unknown_initials(self, text: str, entities: Dict) -> List[Dict]:
        """
        Detect initials that aren't in known aliases.

        Args:
            text: Document text
            entities: Extracted entities (for potential expansion)

        Returns:
            List of unknown initials
        """
        initials = []

        # Find potential initials (2-3 capital letters)
        pattern = r'\b([A-Z]\.?[A-Z]\.?(?:[A-Z]\.?)?)\b'
        matches = re.finditer(pattern, text)

        initial_counts = Counter()
        for match in matches:
            term = match.group(1)
            # Remove periods for consistency
            normalized = term.replace('.', '')

            # Skip if known alias
            if normalized in self.KNOWN_ALIASES:
                continue

            initial_counts[normalized] += 1

        # Report unknown initials with multiple occurrences
        for term, count in initial_counts.items():
            if count >= 2:
                # Try to expand based on entities
                expansion = self._try_expand_initials(term, entities)

                initials.append({
                    'term': term,
                    'likely_refers_to': expansion or 'unknown person (initials)',
                    'confidence_score': 0.7 if expansion else 0.4,
                    'pattern_type': 'initials',
                    'context_snippets': self._extract_contexts(text, term, max_contexts=2),
                    'occurrences': count,
                })

        return initials

    def _detect_quoted_terms(self, text: str) -> List[Dict]:
        """
        Detect unusual quoted terms that may be code words.

        Args:
            text: Document text

        Returns:
            List of quoted terms
        """
        quoted = []

        # Find quoted terms
        pattern = r'"([^"]{3,30})"'
        matches = re.finditer(pattern, text)

        for match in matches:
            term = match.group(1)

            # Skip common phrases
            if term.lower().startswith(('i ', 'the ', 'we ', 'you ', 'he ', 'she ')):
                continue

            quoted.append({
                'term': term,
                'likely_refers_to': 'potential code phrase (quoted)',
                'confidence_score': 0.65,
                'pattern_type': 'quoted_term',
                'context_snippets': self._extract_contexts(text, term, max_contexts=1),
                'occurrences': 1,
            })

        return quoted

    def _try_expand_initials(
        self,
        initials: str,
        entities: Dict
    ) -> str:
        """
        Try to expand initials to full name using entities.

        Args:
            initials: Initials (e.g., "JD")
            entities: Extracted entities

        Returns:
            Expanded name or None
        """
        if len(initials) < 2:
            return None

        # Get all person entities
        persons = entities.get('persons', [])

        # Try to match initials to person names
        for person in persons:
            name_parts = person['text'].split()

            if len(name_parts) >= len(initials):
                # Check if initials match
                name_initials = ''.join([part[0] for part in name_parts[:len(initials)]])

                if name_initials.upper() == initials.upper():
                    return person['text']

        return None

    def _infer_euphemism_meaning(
        self,
        term: str,
        contexts: List[str]
    ) -> str:
        """
        Infer likely meaning of euphemism based on context.

        Args:
            term: Euphemism term
            contexts: Context snippets

        Returns:
            Inferred meaning
        """
        # Mapping of euphemisms to likely meanings
        euphemism_map = {
            'massage': 'sexual abuse/exploitation (euphemism)',
            'modeling': 'recruitment/trafficking (euphemism)',
            'recruitment': 'trafficking (euphemism)',
            'entertainment': 'sexual services (euphemism)',
            'guest': 'victim/target (euphemism)',
            'assistant': 'recruiter/accomplice (euphemism)',
            'introduction': 'provision of victim (euphemism)',
            'appointment': 'abuse session (euphemism)',
            'session': 'abuse event (euphemism)',
        }

        return euphemism_map.get(term.lower(), f'suspicious term (context: {term})')

    def _extract_contexts(
        self,
        text: str,
        term: str,
        max_contexts: int = 3,
        context_window: int = 80
    ) -> List[str]:
        """
        Extract context snippets around term occurrences.

        Args:
            text: Full text
            term: Term to find
            max_contexts: Maximum number of contexts to return
            context_window: Characters before/after term

        Returns:
            List of context snippets
        """
        contexts = []

        pattern = r'\b' + re.escape(term) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for i, match in enumerate(matches):
            if i >= max_contexts:
                break

            start_pos = max(0, match.start() - context_window)
            end_pos = min(len(text), match.end() + context_window)

            context = text[start_pos:end_pos].strip()

            # Clean up context
            context = ' '.join(context.split())  # Normalize whitespace

            contexts.append(f"...{context}...")

        return contexts

    def serialize_code_analysis(self, analysis: Dict) -> str:
        """
        Serialize code analysis to JSON string.

        Args:
            analysis: Code analysis results

        Returns:
            JSON string
        """
        return json.dumps(analysis, ensure_ascii=False)

    def deserialize_code_analysis(self, json_str: str) -> Dict:
        """
        Deserialize code analysis from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Code analysis dictionary
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to deserialize code analysis")
            return {
                'code_terms': [],
                'aliases': [],
                'initials': [],
                'detection_metadata': {}
            }


if __name__ == "__main__":
    # Test code breaking
    logging.basicConfig(level=logging.INFO)

    print("Testing CodeBreaker...")
    print()

    breaker = CodeBreaker()

    # Test text with various code patterns
    test_text = """
    From: JE <jepstein@example.com>
    To: GM <gmax@example.com>
    Subject: Arrangements for weekend

    Please arrange for three new "assistants" to be available for
    the guests this weekend. BC and PA both requested massage
    appointments for Saturday evening.

    The modeling recruitment from last month was very successful.
    SK will bring them to the Island for the special session.

    NM is handling transportation. Flight N212JE departs TEB at 3pm.

    Please ensure all "entertainment" arrangements are confirmed.
    The SPECIAL GUESTS arrive Friday.

    - JE
    """

    # Mock entities
    test_entities = {
        'persons': [
            {'text': 'Jeffrey Epstein', 'count': 1, 'confidence': 0.95},
            {'text': 'Ghislaine Maxwell', 'count': 1, 'confidence': 0.94},
            {'text': 'Sarah Kellen', 'count': 1, 'confidence': 0.90},
        ],
    }

    # Detect code terms
    analysis = breaker.detect_code_terms(
        text=test_text,
        entities=test_entities,
        doc_id="test_doc_001"
    )

    print("Code Breaking Analysis:")
    print("=" * 70)

    print(f"\nAliases Detected ({len(analysis['aliases'])}):")
    for alias in analysis['aliases']:
        print(f"  • {alias['term']} → {alias['likely_refers_to']}")
        print(f"    Confidence: {alias['confidence_score']}, Occurrences: {alias['occurrences']}")

    print(f"\nCode Terms/Euphemisms Detected ({len(analysis['code_terms'])}):")
    for term in analysis['code_terms'][:5]:
        print(f"  • {term['term']} → {term['likely_refers_to']}")
        print(f"    Confidence: {term['confidence_score']}, Pattern: {term['pattern_type']}")
        if term['context_snippets']:
            print(f"    Context: {term['context_snippets'][0][:60]}...")

    print(f"\nUnknown Initials ({len(analysis['initials'])}):")
    for initial in analysis['initials']:
        print(f"  • {initial['term']} → {initial['likely_refers_to']}")
        print(f"    Confidence: {initial['confidence_score']}, Occurrences: {initial['occurrences']}")

    # Test serialization
    print("\n" + "=" * 70)
    print("Testing serialization...")
    json_str = breaker.serialize_code_analysis(analysis)
    print(f"✓ Serialized to {len(json_str)} chars")

    deserialized = breaker.deserialize_code_analysis(json_str)
    print(f"✓ Deserialized {len(deserialized['code_terms'])} code terms")
