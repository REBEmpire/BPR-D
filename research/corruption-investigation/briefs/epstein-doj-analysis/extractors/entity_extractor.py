"""
Named Entity Recognition (NER) for document analysis.

Extracts and categorizes entities:
- PERSON: Names of individuals
- ORG: Organizations, companies, institutions
- GPE: Geographic/political entities (countries, cities, islands)
- DATE: Temporal references

Uses spaCy as primary model with optional ensemble support.
"""
import logging
from typing import Dict, List, Set
from collections import defaultdict
import json

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available - NER will be disabled")

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extract named entities from document text.

    Primary model: spaCy en_core_web_lg (fast, accurate)
    Optional: Ensemble with transformer models for critical docs
    """

    # Entity types we care about for investigation
    TARGET_ENTITY_TYPES = {'PERSON', 'ORG', 'GPE', 'DATE', 'LOC', 'FAC'}

    # Known entities from Epstein case for confidence boosting
    KNOWN_ENTITIES = {
        'PERSON': {
            'Jeffrey Epstein', 'Ghislaine Maxwell', 'Prince Andrew',
            'Bill Clinton', 'Donald Trump', 'Alan Dershowitz',
            'Virginia Giuffre', 'Sarah Kellen', 'Nadia Marcinkova',
        },
        'ORG': {
            'FBI', 'DOJ', 'Department of Justice', 'Federal Bureau of Investigation',
            'Southern District of New York', 'SDNY', 'Victoria\'s Secret',
            'J. Epstein & Co.', 'Financial Trust Company',
        },
        'GPE': {
            'Little St. James', 'St. Thomas', 'US Virgin Islands', 'USVI',
            'New Mexico', 'New York', 'Palm Beach', 'Florida',
            'Manhattan', 'Paris', 'London',
        },
        'LOC': {
            'Zorro Ranch', 'Little St. James Island', 'Great St. James',
            '9 East 71st Street', 'Palm Beach mansion',
        },
    }

    def __init__(self, model_name: str = "en_core_web_lg"):
        """
        Initialize entity extractor.

        Args:
            model_name: spaCy model to use (default: en_core_web_lg)
        """
        self.model_name = model_name
        self.nlp = None

        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.warning(
                    f"Model {model_name} not found. "
                    f"Install with: python -m spacy download {model_name}"
                )
        else:
            logger.warning("spaCy not installed - NER disabled")

    def extract_entities(self, text: str, doc_id: str = None) -> Dict:
        """
        Extract named entities from text.

        Args:
            text: Document text to analyze
            doc_id: Optional document ID for logging

        Returns:
            Dictionary with entity categories and metadata:
            {
                'persons': [{'text': 'John Doe', 'count': 5, 'confidence': 0.95}, ...],
                'organizations': [...],
                'locations': [...],
                'dates': [...],
                'extraction_metadata': {
                    'total_entities': 42,
                    'model_used': 'en_core_web_lg',
                    'confidence_threshold': 0.5,
                }
            }
        """
        if not self.nlp:
            logger.warning(f"NER not available - returning empty results for {doc_id}")
            return self._empty_results()

        logger.info(f"Extracting entities from {doc_id or 'document'}")

        # Process text with spaCy
        doc = self.nlp(text[:1000000])  # Limit to 1M chars for performance

        # Collect entities by type
        entity_collections = defaultdict(lambda: defaultdict(int))

        for ent in doc.ents:
            if ent.label_ in self.TARGET_ENTITY_TYPES:
                # Normalize entity text
                entity_text = self._normalize_entity(ent.text)

                # Map to our categories
                category = self._map_entity_category(ent.label_)

                # Count occurrences
                entity_collections[category][entity_text] += 1

        # Build structured results with confidence scores
        results = {
            'persons': self._build_entity_list(
                entity_collections['persons'],
                'PERSON'
            ),
            'organizations': self._build_entity_list(
                entity_collections['organizations'],
                'ORG'
            ),
            'locations': self._build_entity_list(
                entity_collections['locations'],
                'GPE'
            ),
            'dates': self._build_entity_list(
                entity_collections['dates'],
                'DATE'
            ),
            'extraction_metadata': {
                'total_entities': sum(
                    len(entities) for entities in entity_collections.values()
                ),
                'model_used': self.model_name,
                'confidence_threshold': 0.5,
                'doc_id': doc_id,
            }
        }

        logger.info(
            f"Extracted {results['extraction_metadata']['total_entities']} entities: "
            f"{len(results['persons'])} persons, "
            f"{len(results['organizations'])} orgs, "
            f"{len(results['locations'])} locations, "
            f"{len(results['dates'])} dates"
        )

        return results

    def _build_entity_list(
        self,
        entity_counts: Dict[str, int],
        entity_type: str
    ) -> List[Dict]:
        """
        Build sorted list of entities with confidence scores.

        Args:
            entity_counts: Dict mapping entity text to occurrence count
            entity_type: Type of entity (for known entity matching)

        Returns:
            List of dicts with text, count, confidence
        """
        entities = []

        for text, count in entity_counts.items():
            # Calculate confidence score
            confidence = self._calculate_confidence(text, count, entity_type)

            # Only include if meets threshold
            if confidence >= 0.5:
                entities.append({
                    'text': text,
                    'count': count,
                    'confidence': round(confidence, 2),
                })

        # Sort by count (descending)
        entities.sort(key=lambda x: x['count'], reverse=True)

        return entities

    def _calculate_confidence(
        self,
        entity_text: str,
        count: int,
        entity_type: str
    ) -> float:
        """
        Calculate confidence score for entity.

        Factors:
        - Occurrence count (more = higher confidence)
        - Known entity match (exact match = +0.3 boost)
        - Length (very short = penalty)

        Args:
            entity_text: Entity text
            count: Number of occurrences
            entity_type: Type of entity

        Returns:
            Confidence score 0.0-1.0
        """
        # Base confidence from spaCy (assume 0.7)
        confidence = 0.7

        # Boost for multiple occurrences
        if count >= 5:
            confidence += 0.15
        elif count >= 3:
            confidence += 0.10
        elif count >= 2:
            confidence += 0.05

        # Boost for known entities
        if entity_type in self.KNOWN_ENTITIES:
            if entity_text in self.KNOWN_ENTITIES[entity_type]:
                confidence += 0.3

        # Penalty for very short entities (likely errors)
        if len(entity_text) <= 2:
            confidence -= 0.3

        # Clamp to 0-1 range
        return max(0.0, min(1.0, confidence))

    def _normalize_entity(self, text: str) -> str:
        """
        Normalize entity text.

        Args:
            text: Raw entity text

        Returns:
            Normalized text
        """
        # Strip whitespace
        text = text.strip()

        # Remove excessive whitespace
        text = ' '.join(text.split())

        return text

    def _map_entity_category(self, spacy_label: str) -> str:
        """
        Map spaCy entity label to our categories.

        Args:
            spacy_label: spaCy NER label

        Returns:
            Category name
        """
        mapping = {
            'PERSON': 'persons',
            'ORG': 'organizations',
            'GPE': 'locations',
            'LOC': 'locations',
            'FAC': 'locations',
            'DATE': 'dates',
        }

        return mapping.get(spacy_label, 'other')

    def _empty_results(self) -> Dict:
        """Return empty results structure."""
        return {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'extraction_metadata': {
                'total_entities': 0,
                'model_used': 'none',
                'confidence_threshold': 0.5,
                'error': 'NER not available',
            }
        }

    def serialize_entities(self, entities: Dict) -> str:
        """
        Serialize entities to JSON string for HF dataset storage.

        Args:
            entities: Entity extraction results

        Returns:
            JSON string
        """
        return json.dumps(entities, ensure_ascii=False)

    def deserialize_entities(self, json_str: str) -> Dict:
        """
        Deserialize entities from JSON string.

        Args:
            json_str: JSON string from HF dataset

        Returns:
            Entity dictionary
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to deserialize entities")
            return self._empty_results()


if __name__ == "__main__":
    # Test entity extraction
    logging.basicConfig(level=logging.INFO)

    print("Testing EntityExtractor...")
    print()

    extractor = EntityExtractor()

    if extractor.nlp:
        # Test text with known Epstein case entities
        test_text = """
        From: Jeffrey Epstein <jepstein@example.com>
        To: Ghislaine Maxwell <gmax@example.com>
        Subject: Flight to Little St. James
        Date: July 15, 1998

        Meeting with Prince Andrew at the island next week.
        Bill Clinton may join us. Contact Sarah Kellen to arrange
        transportation from Manhattan to St. Thomas.

        The FBI and DOJ are requesting documents for Case No. 08-cv-80736.
        Victoria's Secret event in Palm Beach on the 20th.
        """

        results = extractor.extract_entities(test_text, doc_id="test_doc_001")

        print("Extraction Results:")
        print("-" * 70)
        print(f"Total entities: {results['extraction_metadata']['total_entities']}")
        print()

        print(f"Persons ({len(results['persons'])}):")
        for entity in results['persons'][:5]:
            print(f"  • {entity['text']} (count: {entity['count']}, conf: {entity['confidence']})")
        print()

        print(f"Organizations ({len(results['organizations'])}):")
        for entity in results['organizations'][:5]:
            print(f"  • {entity['text']} (count: {entity['count']}, conf: {entity['confidence']})")
        print()

        print(f"Locations ({len(results['locations'])}):")
        for entity in results['locations'][:5]:
            print(f"  • {entity['text']} (count: {entity['count']}, conf: {entity['confidence']})")
        print()

        print(f"Dates ({len(results['dates'])}):")
        for entity in results['dates'][:5]:
            print(f"  • {entity['text']} (count: {entity['count']}, conf: {entity['confidence']})")

        # Test serialization
        print()
        print("Testing serialization...")
        json_str = extractor.serialize_entities(results)
        print(f"✓ Serialized to {len(json_str)} chars")

        deserialized = extractor.deserialize_entities(json_str)
        print(f"✓ Deserialized {deserialized['extraction_metadata']['total_entities']} entities")

    else:
        print("❌ spaCy model not available")
        print("Install with: python -m spacy download en_core_web_lg")
