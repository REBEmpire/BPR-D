"""
Location-based activity analysis.

Tracks and analyzes activities at key locations:
- Little St. James Island (USVI)
- Zorro Ranch (New Mexico)
- Manhattan residence (9 East 71st St)
- Palm Beach mansion
- Paris apartment
- London residence
- Other properties

Investigation focus: What happened at these locations?
"""
import logging
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class LocationAnalyzer:
    """
    Analyze location-specific activities and patterns.

    Tracks:
    - Visitor logs for each location
    - Event frequencies
    - Time periods of activity
    - Cross-location patterns
    """

    # Key properties to track
    KEY_LOCATIONS = {
        'little_st_james': {
            'names': [
                'Little St. James', 'Little St James', 'LSJ',
                'St. James Island', 'the Island', 'TIST',  # Airport code
            ],
            'type': 'island',
            'location': 'US Virgin Islands',
        },
        'great_st_james': {
            'names': [
                'Great St. James', 'Great St James', 'GSJ',
            ],
            'type': 'island',
            'location': 'US Virgin Islands',
        },
        'zorro_ranch': {
            'names': [
                'Zorro Ranch', 'New Mexico ranch', 'NM ranch',
                'Stanley', 'New Mexico property',
            ],
            'type': 'ranch',
            'location': 'New Mexico',
        },
        'manhattan': {
            'names': [
                '9 East 71st', '71st Street', 'Manhattan residence',
                'Manhattan townhouse', 'New York residence',
            ],
            'type': 'residence',
            'location': 'Manhattan, New York',
        },
        'palm_beach': {
            'names': [
                'Palm Beach', 'Palm Beach mansion', 'Florida residence',
                'El Brillo Way',
            ],
            'type': 'residence',
            'location': 'Palm Beach, Florida',
        },
        'paris': {
            'names': [
                'Paris apartment', 'Paris residence', 'Avenue Foch',
            ],
            'type': 'residence',
            'location': 'Paris, France',
        },
        'london': {
            'names': [
                'London residence', 'London flat', 'Belgravia',
            ],
            'type': 'residence',
            'location': 'London, UK',
        },
    }

    def __init__(self):
        """Initialize location analyzer."""
        logger.info("LocationAnalyzer initialized")

    def analyze_location_activities(
        self,
        entities: Dict,
        timeline_events: List[Dict],
        doc_id: str = None
    ) -> Dict:
        """
        Analyze location-specific activities from document.

        Args:
            entities: Extracted entities
            timeline_events: Timeline events
            doc_id: Document identifier

        Returns:
            Dictionary of location activities:
            {
                'little_st_james': {
                    'visitors': ['Jeffrey Epstein', 'Prince Andrew', ...],
                    'event_count': 15,
                    'event_types': {'flight': 5, 'meeting': 10},
                    'date_range': {'earliest': '1998-07-15', 'latest': '2019-01-20'},
                    'key_events': [...],
                },
                ...
            }
        """
        logger.info(f"Analyzing location activities from {doc_id or 'document'}")

        # Initialize location activity tracking
        location_activities = defaultdict(lambda: {
            'visitors': set(),
            'event_count': 0,
            'event_types': defaultdict(int),
            'dates': [],
            'key_events': [],
        })

        # Process timeline events
        for event in timeline_events:
            # Identify which key locations are mentioned
            event_locations = event.get('locations', [])

            for location_name in event_locations:
                # Map to key location
                key_location = self._identify_key_location(location_name)

                if key_location:
                    # Track visitors
                    location_activities[key_location]['visitors'].update(
                        event.get('participants', [])
                    )

                    # Track event
                    location_activities[key_location]['event_count'] += 1
                    location_activities[key_location]['event_types'][event.get('event_type', 'unknown')] += 1
                    location_activities[key_location]['dates'].append(event.get('date'))

                    # Store key events (high-profile participants)
                    if self._is_key_event(event):
                        location_activities[key_location]['key_events'].append({
                            'date': event.get('date'),
                            'description': event.get('description'),
                            'participants': event.get('participants', []),
                            'event_type': event.get('event_type'),
                        })

        # Build final structure with metadata
        results = {}

        for location_key, data in location_activities.items():
            # Calculate date range
            dates = [d for d in data['dates'] if d]
            date_range = None
            if dates:
                sorted_dates = sorted(dates)
                date_range = {
                    'earliest': sorted_dates[0],
                    'latest': sorted_dates[-1],
                }

            # Convert sets to lists for JSON serialization
            results[location_key] = {
                'visitors': list(data['visitors']),
                'visitor_count': len(data['visitors']),
                'event_count': data['event_count'],
                'event_types': dict(data['event_types']),
                'date_range': date_range,
                'key_events': data['key_events'][:10],  # Limit to top 10
                'location_info': self.KEY_LOCATIONS[location_key],
            }

        logger.info(
            f"Analyzed {len(results)} key locations with "
            f"{sum(r['event_count'] for r in results.values())} total events"
        )

        return {
            'location_activities': results,
            'analysis_metadata': {
                'locations_tracked': len(results),
                'source_doc': doc_id,
            }
        }

    def _identify_key_location(self, location_name: str) -> str:
        """
        Identify which key location a name refers to.

        Args:
            location_name: Location name from entity extraction

        Returns:
            Key location identifier or None
        """
        location_lower = location_name.lower()

        for key, config in self.KEY_LOCATIONS.items():
            for name_variant in config['names']:
                if name_variant.lower() in location_lower:
                    return key

        return None

    def _is_key_event(self, event: Dict) -> bool:
        """
        Determine if event is significant enough to highlight.

        Args:
            event: Timeline event

        Returns:
            True if key event
        """
        # High-profile participant names
        key_names = {
            'Prince Andrew', 'Bill Clinton', 'Donald Trump',
            'Alan Dershowitz', 'Les Wexner',
        }

        participants = set(event.get('participants', []))

        # Check if any key names present
        if participants & key_names:
            return True

        # Check event type
        if event.get('event_type') in {'legal', 'deposition', 'arrest'}:
            return True

        # Check for multiple participants (meetings)
        if len(participants) >= 3:
            return True

        return False

    def consolidate_location_data(
        self,
        activity_batches: List[Dict]
    ) -> Dict:
        """
        Consolidate location activities across multiple documents.

        Called by CrossDocumentCoordinator during batch processing.

        Args:
            activity_batches: List of location activity results

        Returns:
            Consolidated location intelligence
        """
        logger.info(f"Consolidating {len(activity_batches)} location activity batches")

        # Aggregate data per location
        consolidated = defaultdict(lambda: {
            'visitors': set(),
            'event_count': 0,
            'event_types': defaultdict(int),
            'dates': [],
            'key_events': [],
        })

        for batch in activity_batches:
            location_data = batch.get('location_activities', {})

            for location_key, data in location_data.items():
                # Merge visitors
                consolidated[location_key]['visitors'].update(data.get('visitors', []))

                # Aggregate counts
                consolidated[location_key]['event_count'] += data.get('event_count', 0)

                # Merge event types
                for event_type, count in data.get('event_types', {}).items():
                    consolidated[location_key]['event_types'][event_type] += count

                # Collect dates
                if data.get('date_range'):
                    consolidated[location_key]['dates'].extend([
                        data['date_range']['earliest'],
                        data['date_range']['latest'],
                    ])

                # Collect key events
                consolidated[location_key]['key_events'].extend(
                    data.get('key_events', [])
                )

        # Build final consolidated structure
        results = {}

        for location_key, data in consolidated.items():
            # Calculate overall date range
            dates = [d for d in data['dates'] if d]
            date_range = None
            if dates:
                sorted_dates = sorted(dates)
                date_range = {
                    'earliest': sorted_dates[0],
                    'latest': sorted_dates[-1],
                    'span_years': self._calculate_year_span(sorted_dates[0], sorted_dates[-1]),
                }

            # Sort key events by date
            key_events = sorted(
                data['key_events'],
                key=lambda x: x.get('date', ''),
                reverse=True
            )

            results[location_key] = {
                'visitors': list(data['visitors']),
                'visitor_count': len(data['visitors']),
                'total_events': data['event_count'],
                'event_types': dict(data['event_types']),
                'date_range': date_range,
                'key_events': key_events[:20],  # Top 20 events
                'location_info': self.KEY_LOCATIONS.get(location_key, {}),
            }

        logger.info(
            f"Consolidated data for {len(results)} locations"
        )

        return {
            'consolidated_locations': results,
            'summary': {
                'total_locations': len(results),
                'total_visitors': sum(r['visitor_count'] for r in results.values()),
                'total_events': sum(r['total_events'] for r in results.values()),
            }
        }

    def _calculate_year_span(self, earliest: str, latest: str) -> int:
        """
        Calculate span in years between two dates.

        Args:
            earliest: ISO date string
            latest: ISO date string

        Returns:
            Year span
        """
        try:
            early = datetime.fromisoformat(earliest[:10])
            late = datetime.fromisoformat(latest[:10])
            return late.year - early.year
        except:
            return 0

    def serialize_location_analysis(self, analysis: Dict) -> str:
        """
        Serialize location analysis to JSON string.

        Args:
            analysis: Location analysis results

        Returns:
            JSON string
        """
        # Convert sets to lists for JSON serialization
        serializable = self._make_serializable(analysis)
        return json.dumps(serializable, ensure_ascii=False)

    def deserialize_location_analysis(self, json_str: str) -> Dict:
        """
        Deserialize location analysis from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Location analysis dictionary
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to deserialize location analysis")
            return {
                'location_activities': {},
                'analysis_metadata': {}
            }

    def _make_serializable(self, obj):
        """Recursively convert sets to lists for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj


if __name__ == "__main__":
    # Test location analysis
    logging.basicConfig(level=logging.INFO)

    print("Testing LocationAnalyzer...")
    print()

    analyzer = LocationAnalyzer()

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
            'participants': ['Jeffrey Epstein', 'Prince Andrew'],
            'locations': ['Little St. James Island'],
        },
        {
            'date': '2002-03-10',
            'event_type': 'flight',
            'participants': ['Jeffrey Epstein', 'Bill Clinton'],
            'locations': ['Zorro Ranch'],
        },
        {
            'date': '2005-06-15',
            'event_type': 'legal',
            'participants': ['Jeffrey Epstein'],
            'locations': ['Palm Beach'],
        },
        {
            'date': '2008-01-10',
            'event_type': 'meeting',
            'participants': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
            'locations': ['Manhattan residence'],
        },
    ]

    # Mock entities
    test_entities = {
        'locations': [
            {'text': 'Little St. James', 'count': 3},
            {'text': 'Zorro Ranch', 'count': 1},
            {'text': 'Palm Beach', 'count': 1},
            {'text': 'Manhattan residence', 'count': 1},
        ],
    }

    # Analyze locations
    analysis = analyzer.analyze_location_activities(
        entities=test_entities,
        timeline_events=test_events,
        doc_id="test_doc_001"
    )

    print("Location Analysis Results:")
    print("=" * 70)

    for location_key, data in analysis['location_activities'].items():
        print(f"\n{location_key.upper().replace('_', ' ')}:")
        print(f"  Location: {data['location_info']['location']}")
        print(f"  Type: {data['location_info']['type']}")
        print(f"  Visitor count: {data['visitor_count']}")
        print(f"  Total events: {data['event_count']}")

        if data['date_range']:
            print(f"  Active period: {data['date_range']['earliest']} to {data['date_range']['latest']}")

        print(f"  Event breakdown:")
        for event_type, count in data['event_types'].items():
            print(f"    - {event_type}: {count}")

        if data['key_events']:
            print(f"  Key events:")
            for event in data['key_events'][:3]:
                print(f"    • {event['date']}: {event['description']}")

    # Test consolidation
    print("\n" + "=" * 70)
    print("Testing consolidation...")

    # Create second batch
    analysis2 = analyzer.analyze_location_activities(
        entities=test_entities,
        timeline_events=test_events[:2],
        doc_id="test_doc_002"
    )

    # Consolidate
    consolidated = analyzer.consolidate_location_data([analysis, analysis2])

    print(f"\nConsolidated Summary:")
    print(f"  Total locations tracked: {consolidated['summary']['total_locations']}")
    print(f"  Total unique visitors: {consolidated['summary']['total_visitors']}")
    print(f"  Total events: {consolidated['summary']['total_events']}")

    # Test serialization
    print("\n" + "=" * 70)
    print("Testing serialization...")
    json_str = analyzer.serialize_location_analysis(analysis)
    print(f"✓ Serialized to {len(json_str)} chars")

    deserialized = analyzer.deserialize_location_analysis(json_str)
    print(f"✓ Deserialized {len(deserialized['location_activities'])} locations")
