"""
Entity disambiguation and alias resolution.

Resolves:
- Name variations (Jeffrey Epstein vs J. Epstein vs JE)
- Nicknames and aliases
- Misspellings
- Fuzzy matching across documents

Used by CrossDocumentCoordinator for entity consolidation.
"""
import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import difflib
import re

logger = logging.getLogger(__name__)


class AliasResolver:
    """
    Resolve entity aliases and disambiguate names across documents.

    Strategies:
    1. Exact matching
    2. Fuzzy string matching (edit distance)
    3. Initials expansion
    4. Known alias mapping
    5. Co-occurrence clustering
    """

    # Known canonical names (ground truth)
    CANONICAL_NAMES = {
        'Jeffrey Epstein': [
            'Jeffrey Epstein', 'Jeff Epstein', 'J. Epstein',
            'Epstein', 'JE', 'Jeffrey E. Epstein',
        ],
        'Ghislaine Maxwell': [
            'Ghislaine Maxwell', 'G. Maxwell', 'GM', 'GMax',
            'Maxwell', 'Ghislaine Noelle Marion Maxwell',
        ],
        'Prince Andrew': [
            'Prince Andrew', 'Andrew Windsor', 'Duke of York',
            'PA', 'Andrew', 'Prince Andrew, Duke of York',
        ],
        'Bill Clinton': [
            'Bill Clinton', 'William Clinton', 'BC', 'WJC',
            'William Jefferson Clinton', 'Clinton',
        ],
        'Donald Trump': [
            'Donald Trump', 'Donald J. Trump', 'DJT', 'Trump',
            'Donald John Trump',
        ],
        'Alan Dershowitz': [
            'Alan Dershowitz', 'A. Dershowitz', 'AD', 'Dershowitz',
            'Alan M. Dershowitz',
        ],
        'Sarah Kellen': [
            'Sarah Kellen', 'S. Kellen', 'SK', 'Kellen',
            'Sarah Kensington',
        ],
        'Nadia Marcinkova': [
            'Nadia Marcinkova', 'N. Marcinkova', 'NM', 'Marcinkova',
            'Nadia Marcinko',
        ],
        'Virginia Giuffre': [
            'Virginia Giuffre', 'Virginia Roberts', 'V. Giuffre',
            'V. Roberts', 'VG', 'VR',
        ],
    }

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize alias resolver.

        Args:
            similarity_threshold: Minimum similarity for fuzzy matching (0-1)
        """
        self.similarity_threshold = similarity_threshold

        # Build reverse lookup (alias -> canonical)
        self.alias_to_canonical = {}
        for canonical, aliases in self.CANONICAL_NAMES.items():
            for alias in aliases:
                self.alias_to_canonical[alias.lower()] = canonical

        logger.info(f"AliasResolver initialized with {len(self.CANONICAL_NAMES)} canonical entities")

    def resolve_entity(self, entity_name: str) -> Tuple[str, float]:
        """
        Resolve entity name to canonical form.

        Args:
            entity_name: Entity name to resolve

        Returns:
            Tuple of (canonical_name, confidence)
        """
        # 1. Exact match (highest confidence)
        if entity_name.lower() in self.alias_to_canonical:
            return self.alias_to_canonical[entity_name.lower()], 1.0

        # 2. Fuzzy match against known aliases
        best_match, confidence = self._fuzzy_match(entity_name)
        if confidence >= self.similarity_threshold:
            return best_match, confidence

        # 3. Initials expansion
        if re.match(r'^[A-Z]{2,3}$', entity_name):
            expansion = self._expand_initials(entity_name)
            if expansion:
                return expansion, 0.75

        # 4. No match - return original with low confidence
        return entity_name, 0.3

    def resolve_entity_batch(
        self,
        entities: List[Dict]
    ) -> List[Dict]:
        """
        Resolve a batch of entities.

        Args:
            entities: List of entity dicts from EntityExtractor

        Returns:
            List of entities with resolved canonical names
        """
        resolved = []

        for entity in entities:
            entity_name = entity.get('text', '')
            canonical, confidence = self.resolve_entity(entity_name)

            resolved_entity = entity.copy()
            resolved_entity['canonical_name'] = canonical
            resolved_entity['alias_confidence'] = confidence

            # Update overall confidence
            original_conf = entity.get('confidence', 0.5)
            resolved_entity['confidence'] = min(original_conf, confidence)

            resolved.append(resolved_entity)

        logger.debug(f"Resolved {len(resolved)} entities")

        return resolved

    def cluster_entities(
        self,
        entity_batches: List[List[Dict]]
    ) -> Dict[str, Dict]:
        """
        Cluster entities across multiple documents.

        Args:
            entity_batches: List of entity lists from multiple documents

        Returns:
            Dictionary mapping canonical names to consolidated entity data:
            {
                'Jeffrey Epstein': {
                    'canonical_name': 'Jeffrey Epstein',
                    'aliases_found': ['JE', 'J. Epstein', ...],
                    'total_occurrences': 42,
                    'document_frequency': 12,  # Appears in 12 documents
                    'confidence': 0.95,
                },
                ...
            }
        """
        logger.info(f"Clustering entities from {len(entity_batches)} document batches")

        # Aggregate by canonical name
        clusters = defaultdict(lambda: {
            'aliases_found': set(),
            'total_occurrences': 0,
            'document_frequency': 0,
            'confidence_scores': [],
        })

        for batch in entity_batches:
            # Track which canonical entities appear in this document
            canonical_in_doc = set()

            for entity in batch:
                # Resolve to canonical
                canonical, confidence = self.resolve_entity(entity.get('text', ''))

                # Add to cluster
                clusters[canonical]['aliases_found'].add(entity.get('text', ''))
                clusters[canonical]['total_occurrences'] += entity.get('count', 1)
                clusters[canonical]['confidence_scores'].append(confidence)

                # Track document appearance
                if canonical not in canonical_in_doc:
                    clusters[canonical]['document_frequency'] += 1
                    canonical_in_doc.add(canonical)

        # Build final structure
        consolidated = {}

        for canonical, data in clusters.items():
            avg_confidence = (
                sum(data['confidence_scores']) / len(data['confidence_scores'])
                if data['confidence_scores'] else 0.5
            )

            consolidated[canonical] = {
                'canonical_name': canonical,
                'aliases_found': list(data['aliases_found']),
                'total_occurrences': data['total_occurrences'],
                'document_frequency': data['document_frequency'],
                'confidence': round(avg_confidence, 2),
            }

        logger.info(f"Clustered into {len(consolidated)} canonical entities")

        return consolidated

    def _fuzzy_match(
        self,
        entity_name: str
    ) -> Tuple[str, float]:
        """
        Fuzzy match entity name against known aliases.

        Args:
            entity_name: Name to match

        Returns:
            Tuple of (best_match_canonical, confidence)
        """
        best_match = None
        best_score = 0.0

        entity_lower = entity_name.lower()

        # Compare against all known aliases
        for canonical, aliases in self.CANONICAL_NAMES.items():
            for alias in aliases:
                # Calculate similarity
                similarity = difflib.SequenceMatcher(
                    None,
                    entity_lower,
                    alias.lower()
                ).ratio()

                if similarity > best_score:
                    best_score = similarity
                    best_match = canonical

        return best_match or entity_name, best_score

    def _expand_initials(self, initials: str) -> str:
        """
        Try to expand initials to full name.

        Args:
            initials: Initials (e.g., "JE")

        Returns:
            Canonical name or None
        """
        initials_upper = initials.upper()

        # Check if initials match any known canonical
        for canonical, aliases in self.CANONICAL_NAMES.items():
            if initials_upper in aliases:
                return canonical

        return None

    def build_alias_map(self) -> Dict[str, str]:
        """
        Build complete alias-to-canonical mapping.

        Returns:
            Dictionary mapping all known aliases to canonical names
        """
        return self.alias_to_canonical.copy()

    def get_canonical_names(self) -> List[str]:
        """
        Get list of all canonical entity names.

        Returns:
            List of canonical names
        """
        return list(self.CANONICAL_NAMES.keys())


if __name__ == "__main__":
    # Test alias resolution
    logging.basicConfig(level=logging.INFO)

    print("Testing AliasResolver...")
    print()

    resolver = AliasResolver()

    # Test single entity resolution
    print("Single Entity Resolution:")
    print("-" * 70)

    test_names = [
        'Jeffrey Epstein',
        'JE',
        'J. Epstein',
        'Epstein',
        'Ghislaine Maxwell',
        'GM',
        'GMax',
        'Prince Andrew',
        'PA',
        'Bill Clinton',
        'BC',
        'Unknown Person',
    ]

    for name in test_names:
        canonical, confidence = resolver.resolve_entity(name)
        status = "✓" if confidence >= 0.8 else "~" if confidence >= 0.5 else "?"
        print(f"{status} {name:20} → {canonical:25} (conf: {confidence:.2f})")

    # Test batch resolution
    print("\n" + "=" * 70)
    print("Batch Entity Resolution:")
    print("-" * 70)

    test_entities = [
        {'text': 'Jeffrey Epstein', 'count': 10, 'confidence': 0.95},
        {'text': 'JE', 'count': 5, 'confidence': 0.80},
        {'text': 'Ghislaine Maxwell', 'count': 8, 'confidence': 0.94},
        {'text': 'GM', 'count': 3, 'confidence': 0.75},
        {'text': 'Prince Andrew', 'count': 2, 'confidence': 0.92},
    ]

    resolved = resolver.resolve_entity_batch(test_entities)

    for entity in resolved:
        print(f"  {entity['text']:20} → {entity['canonical_name']:25} "
              f"(conf: {entity['alias_confidence']:.2f})")

    # Test clustering
    print("\n" + "=" * 70)
    print("Entity Clustering Across Documents:")
    print("-" * 70)

    # Simulate entities from multiple documents
    batch1 = [
        {'text': 'Jeffrey Epstein', 'count': 5},
        {'text': 'Ghislaine Maxwell', 'count': 3},
        {'text': 'Prince Andrew', 'count': 1},
    ]

    batch2 = [
        {'text': 'JE', 'count': 3},
        {'text': 'GM', 'count': 2},
        {'text': 'Bill Clinton', 'count': 1},
    ]

    batch3 = [
        {'text': 'J. Epstein', 'count': 4},
        {'text': 'GMax', 'count': 1},
        {'text': 'BC', 'count': 2},
    ]

    clusters = resolver.cluster_entities([batch1, batch2, batch3])

    for canonical, data in sorted(
        clusters.items(),
        key=lambda x: x[1]['total_occurrences'],
        reverse=True
    ):
        print(f"\n{canonical}:")
        print(f"  Aliases: {', '.join(data['aliases_found'])}")
        print(f"  Total occurrences: {data['total_occurrences']}")
        print(f"  Document frequency: {data['document_frequency']}/3")
        print(f"  Confidence: {data['confidence']}")

    print()
    print("=" * 70)
    print(f"✓ Clustered {len(clusters)} canonical entities")
