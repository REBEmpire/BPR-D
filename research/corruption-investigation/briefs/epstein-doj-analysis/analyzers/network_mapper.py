"""
Network analysis and relationship mapping.

Builds relationship graphs from entity co-occurrences:
- Person-to-person connections
- Person-to-organization affiliations
- Person-to-location associations
- Centrality analysis (key players identification)
- Community detection (groups/networks)

Investigation Goal #2: Map the Players
"""
import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logging.warning("NetworkX not available - network analysis disabled")

logger = logging.getLogger(__name__)


class NetworkMapper:
    """
    Build and analyze relationship networks from entity co-occurrences.

    Uses NetworkX for graph construction and analysis.
    """

    def __init__(self):
        """Initialize network mapper."""
        self.graph = None

        if NETWORKX_AVAILABLE:
            self.graph = nx.Graph()
            logger.info("NetworkMapper initialized with NetworkX")
        else:
            logger.warning("NetworkMapper initialized without NetworkX - limited functionality")

    def build_document_network(
        self,
        entities: Dict,
        timeline_events: List[Dict],
        doc_id: str = None
    ) -> Dict:
        """
        Build network relationships from a single document.

        Args:
            entities: Extracted entities (from EntityExtractor)
            timeline_events: Timeline events (from TimelineBuilder)
            doc_id: Document identifier

        Returns:
            Dictionary of relationships:
            {
                'relationships': [
                    {
                        'source': 'Jeffrey Epstein',
                        'target': 'Ghislaine Maxwell',
                        'relationship_type': 'co-occurrence',
                        'strength': 5,  # Number of co-occurrences
                        'contexts': ['flight', 'meeting'],
                        'source_docs': ['dataset_1_doc_a3f2b9'],
                    },
                    ...
                ],
                'network_stats': {
                    'total_nodes': 42,
                    'total_edges': 87,
                    'key_players': [...],
                }
            }
        """
        logger.info(f"Building network from {doc_id or 'document'}")

        relationships = []

        # 1. Person-to-person co-occurrences from timeline events
        person_pairs = self._extract_person_pairs_from_events(timeline_events)

        for (person1, person2), contexts in person_pairs.items():
            relationships.append({
                'source': person1,
                'target': person2,
                'relationship_type': 'co-occurrence',
                'strength': len(contexts),
                'contexts': list(set(contexts)),
                'source_docs': [doc_id] if doc_id else [],
            })

        # 2. Person-to-location associations
        person_location_pairs = self._extract_person_location_pairs(timeline_events)

        for (person, location), event_types in person_location_pairs.items():
            relationships.append({
                'source': person,
                'target': location,
                'relationship_type': 'visited',
                'strength': len(event_types),
                'contexts': list(set(event_types)),
                'source_docs': [doc_id] if doc_id else [],
            })

        # 3. Person-to-organization (simplified - based on entity proximity)
        # This would be enhanced in cross-document correlation

        logger.info(f"Built network with {len(relationships)} relationships")

        return {
            'relationships': relationships,
            'network_stats': {
                'total_relationships': len(relationships),
                'source_doc': doc_id,
            }
        }

    def merge_networks(
        self,
        network_batches: List[Dict]
    ) -> Dict:
        """
        Merge multiple document networks into master network.

        This is called periodically by CrossDocumentCoordinator.

        Args:
            network_batches: List of document networks to merge

        Returns:
            Merged network with consolidated relationships
        """
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX not available - cannot merge networks")
            return {'relationships': [], 'network_stats': {}}

        logger.info(f"Merging {len(network_batches)} document networks")

        # Build NetworkX graph
        G = nx.Graph()

        # Merge all relationships
        relationship_map = defaultdict(lambda: {
            'strength': 0,
            'contexts': set(),
            'source_docs': set(),
        })

        for batch in network_batches:
            for rel in batch.get('relationships', []):
                # Create edge key
                source = rel['source']
                target = rel['target']
                rel_type = rel['relationship_type']

                edge_key = tuple(sorted([source, target])) + (rel_type,)

                # Aggregate
                relationship_map[edge_key]['strength'] += rel['strength']
                relationship_map[edge_key]['contexts'].update(rel['contexts'])
                relationship_map[edge_key]['source_docs'].update(rel['source_docs'])

                # Add to graph
                G.add_edge(
                    source,
                    target,
                    relationship_type=rel_type,
                    weight=rel['strength']
                )

        # Build consolidated relationships list
        consolidated_relationships = []

        for edge_key, data in relationship_map.items():
            if len(edge_key) == 3:
                source, target, rel_type = edge_key[0], edge_key[1], edge_key[2]
            else:
                continue

            consolidated_relationships.append({
                'source': source,
                'target': target,
                'relationship_type': rel_type,
                'strength': data['strength'],
                'contexts': list(data['contexts']),
                'source_docs': list(data['source_docs']),
            })

        # Sort by strength (strongest first)
        consolidated_relationships.sort(
            key=lambda x: x['strength'],
            reverse=True
        )

        # Calculate network statistics
        network_stats = self._calculate_network_stats(G)

        logger.info(
            f"Merged network: {network_stats['total_nodes']} nodes, "
            f"{network_stats['total_edges']} edges"
        )

        return {
            'relationships': consolidated_relationships,
            'network_stats': network_stats,
        }

    def _extract_person_pairs_from_events(
        self,
        events: List[Dict]
    ) -> Dict[Tuple[str, str], List[str]]:
        """
        Extract person-to-person co-occurrences from timeline events.

        Args:
            events: Timeline events

        Returns:
            Dict mapping (person1, person2) -> [contexts]
        """
        pairs = defaultdict(list)

        for event in events:
            participants = event.get('participants', [])

            # Create pairs from participants in same event
            if len(participants) >= 2:
                for i in range(len(participants)):
                    for j in range(i + 1, len(participants)):
                        person1 = participants[i]
                        person2 = participants[j]

                        # Sort for consistency
                        pair = tuple(sorted([person1, person2]))

                        # Add event type as context
                        pairs[pair].append(event.get('event_type', 'unknown'))

        return pairs

    def _extract_person_location_pairs(
        self,
        events: List[Dict]
    ) -> Dict[Tuple[str, str], List[str]]:
        """
        Extract person-to-location associations from timeline events.

        Args:
            events: Timeline events

        Returns:
            Dict mapping (person, location) -> [event_types]
        """
        pairs = defaultdict(list)

        for event in events:
            participants = event.get('participants', [])
            locations = event.get('locations', [])

            # Create person-location pairs
            for person in participants:
                for location in locations:
                    pair = (person, location)
                    pairs[pair].append(event.get('event_type', 'unknown'))

        return pairs

    def _calculate_network_stats(self, G: "nx.Graph") -> Dict:
        """
        Calculate network statistics and identify key players.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary of network statistics
        """
        if not G or G.number_of_nodes() == 0:
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'key_players': [],
            }

        stats = {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
        }

        # Calculate centrality measures
        try:
            # Degree centrality (most connected)
            degree_centrality = nx.degree_centrality(G)

            # Betweenness centrality (key connectors/brokers)
            betweenness_centrality = nx.betweenness_centrality(G)

            # Identify key players (top 10 by degree centrality)
            sorted_by_degree = sorted(
                degree_centrality.items(),
                key=lambda x: x[1],
                reverse=True
            )

            stats['key_players'] = [
                {
                    'name': node,
                    'degree_centrality': round(degree_centrality[node], 3),
                    'betweenness_centrality': round(betweenness_centrality.get(node, 0), 3),
                    'connections': G.degree(node),
                }
                for node, _ in sorted_by_degree[:10]
            ]

            # Average clustering coefficient
            stats['avg_clustering'] = round(nx.average_clustering(G), 3)

            # Density
            stats['density'] = round(nx.density(G), 3)

        except Exception as e:
            logger.warning(f"Error calculating network stats: {e}")

        return stats

    def export_for_gephi(
        self,
        network: Dict,
        output_format: str = 'gexf'
    ) -> str:
        """
        Export network in format suitable for Gephi visualization.

        Args:
            network: Network dictionary
            output_format: Format (gexf, graphml, gml)

        Returns:
            Graph data as string (XML/GML format)
        """
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX not available - cannot export")
            return ""

        # Build graph from relationships
        G = nx.Graph()

        for rel in network.get('relationships', []):
            G.add_edge(
                rel['source'],
                rel['target'],
                weight=rel['strength'],
                relationship_type=rel['relationship_type'],
                contexts=','.join(rel['contexts']),
            )

        # Export to string
        if output_format == 'gexf':
            from io import BytesIO
            buffer = BytesIO()
            nx.write_gexf(G, buffer)
            return buffer.getvalue().decode('utf-8')
        elif output_format == 'graphml':
            from io import BytesIO
            buffer = BytesIO()
            nx.write_graphml(G, buffer)
            return buffer.getvalue().decode('utf-8')
        else:
            # GML format
            return '\n'.join(nx.generate_gml(G))

    def serialize_network(self, network: Dict) -> str:
        """
        Serialize network to JSON string for HF dataset.

        Args:
            network: Network dictionary

        Returns:
            JSON string
        """
        return json.dumps(network, ensure_ascii=False)

    def deserialize_network(self, json_str: str) -> Dict:
        """
        Deserialize network from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Network dictionary
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to deserialize network")
            return {'relationships': [], 'network_stats': {}}


if __name__ == "__main__":
    # Test network mapping
    logging.basicConfig(level=logging.INFO)

    print("Testing NetworkMapper...")
    print()

    mapper = NetworkMapper()

    if NETWORKX_AVAILABLE:
        # Mock timeline events
        test_events = [
            {
                'date': '1998-07-15',
                'event_type': 'flight',
                'participants': ['Jeffrey Epstein', 'Ghislaine Maxwell', 'Prince Andrew'],
                'locations': ['Little St. James'],
            },
            {
                'date': '1998-07-20',
                'event_type': 'meeting',
                'participants': ['Jeffrey Epstein', 'Bill Clinton'],
                'locations': ['Manhattan'],
            },
            {
                'date': '1998-07-22',
                'event_type': 'flight',
                'participants': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
                'locations': ['Palm Beach'],
            },
            {
                'date': '2008-03-12',
                'event_type': 'legal',
                'participants': ['Jeffrey Epstein', 'Alan Dershowitz'],
                'locations': ['Palm Beach'],
            },
        ]

        # Mock entities
        test_entities = {
            'persons': [
                {'text': 'Jeffrey Epstein', 'count': 10},
                {'text': 'Ghislaine Maxwell', 'count': 5},
                {'text': 'Prince Andrew', 'count': 2},
                {'text': 'Bill Clinton', 'count': 3},
                {'text': 'Alan Dershowitz', 'count': 2},
            ],
            'locations': [
                {'text': 'Little St. James', 'count': 3},
                {'text': 'Manhattan', 'count': 4},
                {'text': 'Palm Beach', 'count': 6},
            ],
        }

        # Build network
        network = mapper.build_document_network(
            entities=test_entities,
            timeline_events=test_events,
            doc_id="test_doc_001"
        )

        print(f"Network Analysis Results:")
        print("-" * 70)
        print(f"Total relationships: {network['network_stats']['total_relationships']}")
        print()

        print("Person-to-Person Relationships:")
        for rel in [r for r in network['relationships'] if r['relationship_type'] == 'co-occurrence'][:5]:
            print(f"  • {rel['source']} ↔ {rel['target']}")
            print(f"    Strength: {rel['strength']}, Contexts: {', '.join(rel['contexts'])}")
        print()

        print("Person-to-Location Associations:")
        for rel in [r for r in network['relationships'] if r['relationship_type'] == 'visited'][:5]:
            print(f"  • {rel['source']} → {rel['target']}")
            print(f"    Visits: {rel['strength']}, Contexts: {', '.join(rel['contexts'])}")
        print()

        # Test network merging
        print("=" * 70)
        print("Testing network merging...")

        # Create second document network
        network2 = mapper.build_document_network(
            entities=test_entities,
            timeline_events=test_events[:2],  # Subset
            doc_id="test_doc_002"
        )

        # Merge networks
        merged = mapper.merge_networks([network, network2])

        print(f"Merged Network:")
        print(f"  Nodes: {merged['network_stats']['total_nodes']}")
        print(f"  Edges: {merged['network_stats']['total_edges']}")
        print(f"  Density: {merged['network_stats'].get('density', 'N/A')}")
        print()

        print("Key Players (by centrality):")
        for player in merged['network_stats'].get('key_players', [])[:5]:
            print(f"  • {player['name']}")
            print(f"    Connections: {player['connections']}")
            print(f"    Degree centrality: {player['degree_centrality']}")
            print(f"    Betweenness centrality: {player['betweenness_centrality']}")

        # Test serialization
        print()
        print("=" * 70)
        print("Testing serialization...")
        json_str = mapper.serialize_network(merged)
        print(f"✓ Serialized to {len(json_str)} chars")

        deserialized = mapper.deserialize_network(json_str)
        print(f"✓ Deserialized {len(deserialized['relationships'])} relationships")

    else:
        print("❌ NetworkX not available")
        print("Install with: pip install networkx")
