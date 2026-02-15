"""
Cross-document correlation and batch processing coordinator.

Orchestrates periodic batch analysis across multiple documents:
- Entity consolidation (alias resolution)
- Network merging (relationship aggregation)
- Timeline consolidation (master timeline)
- Code dictionary building (pattern aggregation)
- Location intelligence (visitor tracking)

Called every N documents (default: 10) to build global intelligence.
"""
import logging
from typing import Dict, List
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from extractors.alias_resolver import AliasResolver
from analyzers.network_mapper import NetworkMapper
from analyzers.location_analyzer import LocationAnalyzer

logger = logging.getLogger(__name__)


class CrossDocumentCoordinator:
    """
    Coordinate cross-document analysis and correlation.

    Aggregates results from multiple documents to build:
    - Master entity index (with aliases resolved)
    - Consolidated relationship network
    - Master timeline
    - Code dictionary
    - Location intelligence database
    """

    def __init__(self, batch_size: int = 10):
        """
        Initialize coordinator.

        Args:
            batch_size: Process batch every N documents (default: 10)
        """
        self.batch_size = batch_size

        # Initialize analyzers
        self.alias_resolver = AliasResolver()
        self.network_mapper = NetworkMapper()
        self.location_analyzer = LocationAnalyzer()

        # Batch accumulators
        self.pending_entities = []
        self.pending_networks = []
        self.pending_timelines = []
        self.pending_code_analyses = []
        self.pending_locations = []

        self.docs_since_last_batch = 0

        logger.info(f"CrossDocumentCoordinator initialized (batch size: {batch_size})")

    def add_document_results(
        self,
        doc_id: str,
        entities: Dict,
        network: Dict,
        timeline_events: List[Dict],
        code_analysis: Dict,
        location_analysis: Dict
    ) -> bool:
        """
        Add document results to batch accumulators.

        Args:
            doc_id: Document identifier
            entities: Entity extraction results
            network: Network analysis results
            timeline_events: Timeline events
            code_analysis: Code breaking results
            location_analysis: Location analysis results

        Returns:
            True if batch processing triggered, False otherwise
        """
        logger.debug(f"Adding document {doc_id} to batch accumulators")

        # Add to accumulators
        self.pending_entities.append(entities)
        self.pending_networks.append(network)
        self.pending_timelines.append(timeline_events)
        self.pending_code_analyses.append(code_analysis)
        self.pending_locations.append(location_analysis)

        self.docs_since_last_batch += 1

        # Check if batch processing needed
        if self.docs_since_last_batch >= self.batch_size:
            logger.info(f"Batch threshold reached ({self.batch_size} docs) - triggering correlation")
            return True

        return False

    def process_batch(self) -> Dict:
        """
        Process accumulated batch of documents.

        Performs cross-document correlation and builds consolidated intelligence.

        Returns:
            Dictionary of consolidated results ready for HF dataset upload:
            {
                'entity_index': {...},  # Consolidated entities with aliases
                'network': {...},  # Merged network graph
                'timeline': [...],  # Consolidated timeline
                'code_dictionary': {...},  # Aggregated code terms
                'location_intelligence': {...},  # Consolidated location data
                'batch_metadata': {...},
            }
        """
        logger.info(f"Processing batch of {self.docs_since_last_batch} documents")

        batch_start = datetime.now()

        # 1. Entity consolidation with alias resolution
        entity_index = self._consolidate_entities()

        # 2. Network merging
        consolidated_network = self.network_mapper.merge_networks(self.pending_networks)

        # 3. Timeline consolidation
        consolidated_timeline = self._consolidate_timeline()

        # 4. Code dictionary building
        code_dictionary = self._build_code_dictionary()

        # 5. Location intelligence consolidation
        location_intelligence = self.location_analyzer.consolidate_location_data(
            self.pending_locations
        )

        # Build results
        results = {
            'entity_index': entity_index,
            'network': consolidated_network,
            'timeline': consolidated_timeline,
            'code_dictionary': code_dictionary,
            'location_intelligence': location_intelligence,
            'batch_metadata': {
                'documents_processed': self.docs_since_last_batch,
                'batch_timestamp': datetime.now().isoformat(),
                'processing_time_seconds': (datetime.now() - batch_start).total_seconds(),
            }
        }

        # Clear accumulators
        self._reset_accumulators()

        logger.info(
            f"Batch processing complete: "
            f"{len(entity_index)} entities, "
            f"{len(consolidated_network.get('relationships', []))} relationships, "
            f"{len(consolidated_timeline)} timeline events"
        )

        return results

    def _consolidate_entities(self) -> Dict:
        """
        Consolidate entities across documents with alias resolution.

        Returns:
            Entity index mapping canonical names to entity data
        """
        logger.debug("Consolidating entities with alias resolution")

        # Extract person entities from all batches
        all_person_entities = []

        for entity_batch in self.pending_entities:
            persons = entity_batch.get('persons', [])
            all_person_entities.append(persons)

        # Cluster entities (resolves aliases)
        clustered = self.alias_resolver.cluster_entities(all_person_entities)

        return clustered

    def _consolidate_timeline(self) -> List[Dict]:
        """
        Consolidate timeline events across documents.

        Returns:
            Sorted list of timeline events
        """
        logger.debug("Consolidating timeline events")

        all_events = []

        for timeline_batch in self.pending_timelines:
            all_events.extend(timeline_batch)

        # Sort by date
        all_events.sort(key=lambda x: x.get('date', ''))

        # Deduplicate similar events (same date, participants, location)
        deduplicated = self._deduplicate_events(all_events)

        logger.debug(f"Consolidated {len(deduplicated)} timeline events")

        return deduplicated

    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """
        Remove duplicate timeline events.

        Args:
            events: List of timeline events

        Returns:
            Deduplicated list
        """
        seen_events = set()
        unique_events = []

        for event in events:
            # Create fingerprint
            fingerprint = (
                event.get('date'),
                tuple(sorted(event.get('participants', []))),
                tuple(sorted(event.get('locations', []))),
                event.get('event_type'),
            )

            if fingerprint not in seen_events:
                seen_events.add(fingerprint)
                unique_events.append(event)

        return unique_events

    def _build_code_dictionary(self) -> Dict:
        """
        Build consolidated code dictionary from all detections.

        Returns:
            Code dictionary mapping terms to likely meanings
        """
        logger.debug("Building consolidated code dictionary")

        # Aggregate all code terms
        term_aggregations = {}

        for code_batch in self.pending_code_analyses:
            # Process aliases
            for alias in code_batch.get('aliases', []):
                term = alias['term']

                if term not in term_aggregations:
                    term_aggregations[term] = {
                        'likely_refers_to': alias['likely_refers_to'],
                        'confidence_scores': [],
                        'context_snippets': [],
                        'source_docs': set(),
                        'total_occurrences': 0,
                    }

                term_aggregations[term]['confidence_scores'].append(alias['confidence_score'])
                term_aggregations[term]['context_snippets'].extend(alias.get('context_snippets', []))
                term_aggregations[term]['source_docs'].add(code_batch.get('detection_metadata', {}).get('source_doc', 'unknown'))
                term_aggregations[term]['total_occurrences'] += alias.get('occurrences', 1)

            # Process code terms
            for code_term in code_batch.get('code_terms', []):
                term = code_term['term']

                if term not in term_aggregations:
                    term_aggregations[term] = {
                        'likely_refers_to': code_term['likely_refers_to'],
                        'confidence_scores': [],
                        'context_snippets': [],
                        'source_docs': set(),
                        'total_occurrences': 0,
                    }

                term_aggregations[term]['confidence_scores'].append(code_term['confidence_score'])
                term_aggregations[term]['context_snippets'].extend(code_term.get('context_snippets', []))
                term_aggregations[term]['source_docs'].add(code_batch.get('detection_metadata', {}).get('source_doc', 'unknown'))
                term_aggregations[term]['total_occurrences'] += code_term.get('occurrences', 1)

        # Build final dictionary
        code_dictionary = {}

        for term, data in term_aggregations.items():
            # Calculate average confidence
            avg_confidence = (
                sum(data['confidence_scores']) / len(data['confidence_scores'])
                if data['confidence_scores'] else 0.5
            )

            # Limit context snippets
            limited_contexts = data['context_snippets'][:5]

            code_dictionary[term] = {
                'code_term': term,
                'likely_refers_to': data['likely_refers_to'],
                'confidence_score': round(avg_confidence, 2),
                'source_docs': list(data['source_docs']),
                'context_snippets': limited_contexts,
                'total_occurrences': data['total_occurrences'],
                'document_frequency': len(data['source_docs']),
            }

        logger.debug(f"Built code dictionary with {len(code_dictionary)} terms")

        return code_dictionary

    def _reset_accumulators(self):
        """Reset batch accumulators after processing."""
        self.pending_entities = []
        self.pending_networks = []
        self.pending_timelines = []
        self.pending_code_analyses = []
        self.pending_locations = []
        self.docs_since_last_batch = 0

        logger.debug("Batch accumulators reset")

    def get_batch_status(self) -> Dict:
        """
        Get status of current batch.

        Returns:
            Status dictionary
        """
        return {
            'documents_in_batch': self.docs_since_last_batch,
            'batch_size': self.batch_size,
            'documents_until_next_batch': self.batch_size - self.docs_since_last_batch,
            'batch_ready': self.docs_since_last_batch >= self.batch_size,
        }


if __name__ == "__main__":
    # Test cross-document coordination
    logging.basicConfig(level=logging.INFO)

    print("Testing CrossDocumentCoordinator...")
    print()

    coordinator = CrossDocumentCoordinator(batch_size=3)

    # Simulate processing 3 documents
    for i in range(1, 4):
        print(f"Adding document {i}...")

        # Mock data
        entities = {
            'persons': [
                {'text': 'Jeffrey Epstein' if i % 2 == 0 else 'JE', 'count': 5, 'confidence': 0.95},
                {'text': 'Ghislaine Maxwell' if i % 3 == 0 else 'GM', 'count': 3, 'confidence': 0.94},
            ],
        }

        network = {
            'relationships': [
                {
                    'source': 'Jeffrey Epstein',
                    'target': 'Ghislaine Maxwell',
                    'relationship_type': 'co-occurrence',
                    'strength': 2,
                    'contexts': ['flight'],
                    'source_docs': [f'doc_{i}'],
                }
            ],
        }

        timeline_events = [
            {
                'date': f'1998-07-{10+i:02d}',
                'event_type': 'flight',
                'participants': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
                'locations': ['Little St. James'],
            }
        ]

        code_analysis = {
            'aliases': [
                {'term': 'JE', 'likely_refers_to': 'Jeffrey Epstein', 'confidence_score': 0.95, 'occurrences': 2},
            ],
            'code_terms': [
                {'term': 'massage', 'likely_refers_to': 'sexual abuse (euphemism)', 'confidence_score': 0.75, 'occurrences': 1},
            ],
            'detection_metadata': {'source_doc': f'doc_{i}'},
        }

        location_analysis = {
            'location_activities': {
                'little_st_james': {
                    'visitors': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
                    'event_count': 1,
                    'event_types': {'flight': 1},
                }
            }
        }

        # Add to coordinator
        batch_ready = coordinator.add_document_results(
            doc_id=f'doc_{i}',
            entities=entities,
            network=network,
            timeline_events=timeline_events,
            code_analysis=code_analysis,
            location_analysis=location_analysis
        )

        status = coordinator.get_batch_status()
        print(f"  Batch status: {status['documents_in_batch']}/{status['batch_size']}")

        if batch_ready:
            print("\n" + "=" * 70)
            print("BATCH PROCESSING TRIGGERED")
            print("=" * 70)

            results = coordinator.process_batch()

            print("\nBatch Results:")
            print(f"  Entities: {len(results['entity_index'])}")
            print(f"  Relationships: {len(results['network']['relationships'])}")
            print(f"  Timeline events: {len(results['timeline'])}")
            print(f"  Code dictionary terms: {len(results['code_dictionary'])}")
            print(f"  Locations tracked: {results['location_intelligence']['summary']['total_locations']}")
            print(f"  Processing time: {results['batch_metadata']['processing_time_seconds']:.2f}s")

            print("\nEntity Index (canonical names):")
            for canonical, data in list(results['entity_index'].items())[:5]:
                print(f"  • {canonical}")
                print(f"    Aliases: {', '.join(data['aliases_found'])}")
                print(f"    Occurrences: {data['total_occurrences']}")

            print("\nCode Dictionary:")
            for term, data in list(results['code_dictionary'].items())[:3]:
                print(f"  • {term} → {data['likely_refers_to']}")
                print(f"    Confidence: {data['confidence_score']}, Docs: {data['document_frequency']}")

    print("\n" + "=" * 70)
    print("✓ Cross-document coordination test complete")
