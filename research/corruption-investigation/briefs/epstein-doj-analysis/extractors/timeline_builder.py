"""
Timeline extraction and event reconstruction.

Builds chronological sequences of events from document analysis:
- Explicit dates (July 15, 1998, 2008-03-12)
- Relative dates (last week, next month)
- Metadata dates (document creation, email sent)
- Event categorization (meetings, flights, communications, legal)

Investigation Goal #3: Master Timeline Reconstruction (1980s-2019)
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import json

logger = logging.getLogger(__name__)


class TimelineBuilder:
    """
    Extract temporal events and build chronological sequences.

    Strategies:
    1. Explicit date extraction (spaCy DATE entities + regex patterns)
    2. Relative date resolution (context-aware)
    3. Metadata date extraction (PDF, email headers)
    4. Event categorization and context capture
    """

    # Date patterns for various formats
    DATE_PATTERNS = [
        # Standard formats
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY, M/D/YY
        r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
        r'\b\d{2}-\d{2}-\d{4}\b',  # DD-MM-YYYY

        # Written formats
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',

        # Year only (for ranges)
        r'\b(19\d{2}|20[0-2]\d)\b',
    ]

    # Relative date patterns
    RELATIVE_PATTERNS = [
        (r'\b(yesterday|today|tomorrow)\b', 'day'),
        (r'\b(last|next|this)\s+(week|month|year)\b', 'period'),
        (r'\b(\d+)\s+(days?|weeks?|months?|years?)\s+ago\b', 'ago'),
        (r'\bin\s+(\d+)\s+(days?|weeks?|months?|years?)\b', 'future'),
    ]

    # Event trigger words for categorization
    EVENT_CATEGORIES = {
        'flight': [
            'flight', 'flew', 'airplane', 'aircraft', 'departed', 'arrived',
            'TEB', 'TIST', 'PBI', 'JFK', 'CDG',  # Airport codes
        ],
        'meeting': [
            'meeting', 'met', 'conference', 'discussed', 'conversation',
            'lunch', 'dinner', 'breakfast', 'visit',
        ],
        'communication': [
            'email', 'called', 'phone', 'message', 'fax', 'letter',
            'spoke', 'correspondence', 'telegram',
        ],
        'legal': [
            'deposition', 'hearing', 'court', 'filed', 'motion', 'subpoena',
            'settlement', 'lawsuit', 'indictment', 'arrest',
        ],
        'transaction': [
            'payment', 'transfer', 'wire', 'check', 'invoice', 'receipt',
            'purchase', 'contract', 'agreement',
        ],
    }

    def __init__(self):
        """Initialize timeline builder."""
        logger.info("TimelineBuilder initialized")

    def extract_timeline_events(
        self,
        text: str,
        entities: Dict,
        metadata: Dict,
        doc_id: str = None
    ) -> List[Dict]:
        """
        Extract temporal events from document.

        Args:
            text: Document text
            entities: Extracted entities from EntityExtractor
            metadata: Document metadata (includes PDF dates, email dates)
            doc_id: Document identifier

        Returns:
            List of timeline events:
            [
                {
                    'date': '1998-07-15',  # ISO format
                    'date_confidence': 0.9,
                    'event_type': 'flight',
                    'description': 'Flight from TEB to TIST',
                    'participants': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
                    'locations': ['Little St. James'],
                    'context_snippet': '...',
                    'source_doc': 'dataset_1_doc_a3f2b9',
                },
                ...
            ]
        """
        logger.info(f"Extracting timeline events from {doc_id or 'document'}")

        events = []

        # 1. Extract explicit dates
        explicit_dates = self._extract_explicit_dates(text)
        logger.debug(f"Found {len(explicit_dates)} explicit dates")

        # 2. Add metadata dates (high confidence)
        metadata_dates = self._extract_metadata_dates(metadata, doc_id)
        events.extend(metadata_dates)

        # 3. Build events from explicit dates
        for date_str, date_obj, confidence, context in explicit_dates:
            # Categorize event based on context
            event_type = self._categorize_event(context)

            # Extract participants and locations from context
            participants = self._extract_participants_from_context(
                context,
                entities.get('persons', [])
            )
            locations = self._extract_locations_from_context(
                context,
                entities.get('locations', [])
            )

            event = {
                'date': date_obj.isoformat()[:10] if date_obj else date_str,
                'date_confidence': confidence,
                'event_type': event_type,
                'description': self._generate_event_description(
                    event_type,
                    context,
                    participants,
                    locations
                ),
                'participants': participants,
                'locations': locations,
                'context_snippet': context[:200],
                'source_doc': doc_id,
            }

            events.append(event)

        # 4. Sort by date
        events.sort(key=lambda x: x['date'])

        logger.info(f"Extracted {len(events)} timeline events")

        return events

    def _extract_explicit_dates(
        self,
        text: str
    ) -> List[Tuple[str, Optional[datetime], float, str]]:
        """
        Extract explicit date mentions from text.

        Returns:
            List of tuples: (date_str, date_obj, confidence, context)
        """
        dates = []

        for pattern in self.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_str = match.group(0)
                start_pos = match.start()

                # Extract context (100 chars before/after)
                context_start = max(0, start_pos - 100)
                context_end = min(len(text), start_pos + 100)
                context = text[context_start:context_end].strip()

                # Try to parse date
                date_obj, confidence = self._parse_date(date_str)

                if date_obj and confidence >= 0.5:
                    dates.append((date_str, date_obj, confidence, context))

        # Deduplicate by date
        seen_dates = set()
        unique_dates = []

        for date_tuple in dates:
            date_key = date_tuple[1].isoformat()[:10] if date_tuple[1] else date_tuple[0]
            if date_key not in seen_dates:
                seen_dates.add(date_key)
                unique_dates.append(date_tuple)

        return unique_dates

    def _parse_date(self, date_str: str) -> Tuple[Optional[datetime], float]:
        """
        Parse date string to datetime object.

        Returns:
            Tuple of (datetime_obj, confidence_score)
        """
        try:
            # Use dateutil parser for flexibility
            dt = date_parser.parse(date_str, fuzzy=True)

            # Confidence based on specificity
            confidence = 0.9

            # Check if date is reasonable (1980-2030)
            if dt.year < 1980 or dt.year > 2030:
                confidence = 0.3

            # Boost confidence for more specific dates
            if date_str.count('/') >= 2 or date_str.count('-') >= 2:
                confidence = 0.95

            return dt, confidence

        except (ValueError, OverflowError):
            # Failed to parse
            return None, 0.0

    def _extract_metadata_dates(
        self,
        metadata: Dict,
        doc_id: str
    ) -> List[Dict]:
        """
        Extract dates from document metadata.

        Args:
            metadata: Document metadata
            doc_id: Document ID

        Returns:
            List of timeline events from metadata
        """
        events = []

        # Extract from nested metadata JSON
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                return events

        # PDF creation date
        pdf_meta = metadata.get('pdf_metadata', {})
        if pdf_meta.get('creation_date'):
            events.append({
                'date': self._normalize_date(pdf_meta['creation_date']),
                'date_confidence': 0.95,
                'event_type': 'document_created',
                'description': 'Document created',
                'participants': [],
                'locations': [],
                'context_snippet': 'PDF metadata',
                'source_doc': doc_id,
            })

        # Email date (if email document)
        # This would be extracted by metadata_extractor in future enhancement

        return events

    def _categorize_event(self, context: str) -> str:
        """
        Categorize event based on context.

        Args:
            context: Text context around date

        Returns:
            Event category
        """
        context_lower = context.lower()

        for category, triggers in self.EVENT_CATEGORIES.items():
            for trigger in triggers:
                if trigger.lower() in context_lower:
                    return category

        return 'unknown'

    def _extract_participants_from_context(
        self,
        context: str,
        all_persons: List[Dict]
    ) -> List[str]:
        """
        Extract participant names mentioned in context.

        Args:
            context: Text context
            all_persons: All persons extracted from document

        Returns:
            List of participant names
        """
        participants = []

        for person in all_persons:
            if person['text'] in context:
                participants.append(person['text'])

        return participants

    def _extract_locations_from_context(
        self,
        context: str,
        all_locations: List[Dict]
    ) -> List[str]:
        """
        Extract locations mentioned in context.

        Args:
            context: Text context
            all_locations: All locations extracted from document

        Returns:
            List of location names
        """
        locations = []

        for location in all_locations:
            if location['text'] in context:
                locations.append(location['text'])

        return locations

    def _generate_event_description(
        self,
        event_type: str,
        context: str,
        participants: List[str],
        locations: List[str]
    ) -> str:
        """
        Generate human-readable event description.

        Args:
            event_type: Type of event
            context: Context text
            participants: Participant names
            locations: Location names

        Returns:
            Event description string
        """
        # Start with event type
        description_parts = [event_type.replace('_', ' ').title()]

        # Add participants
        if participants:
            if len(participants) == 1:
                description_parts.append(f"involving {participants[0]}")
            elif len(participants) == 2:
                description_parts.append(f"involving {participants[0]} and {participants[1]}")
            else:
                description_parts.append(f"involving {participants[0]} and {len(participants)-1} others")

        # Add location
        if locations:
            description_parts.append(f"at {locations[0]}")

        # Join parts
        description = ' '.join(description_parts)

        # Fallback to context snippet
        if description == event_type.replace('_', ' ').title():
            # Extract first sentence from context
            sentences = context.split('.')
            if sentences:
                description = sentences[0].strip()[:100]

        return description

    def _normalize_date(self, date_value) -> str:
        """
        Normalize date to ISO format string.

        Args:
            date_value: Date in various formats

        Returns:
            ISO format date string (YYYY-MM-DD)
        """
        if isinstance(date_value, datetime):
            return date_value.isoformat()[:10]
        elif isinstance(date_value, str):
            try:
                dt = date_parser.parse(date_value)
                return dt.isoformat()[:10]
            except:
                return date_value
        else:
            return str(date_value)

    def serialize_events(self, events: List[Dict]) -> str:
        """
        Serialize timeline events to JSON string.

        Args:
            events: List of timeline events

        Returns:
            JSON string
        """
        return json.dumps(events, ensure_ascii=False)

    def deserialize_events(self, json_str: str) -> List[Dict]:
        """
        Deserialize timeline events from JSON string.

        Args:
            json_str: JSON string

        Returns:
            List of timeline events
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to deserialize timeline events")
            return []


if __name__ == "__main__":
    # Test timeline extraction
    logging.basicConfig(level=logging.INFO)

    print("Testing TimelineBuilder...")
    print()

    builder = TimelineBuilder()

    # Test text with various date formats
    test_text = """
    From: Jeffrey Epstein <jepstein@example.com>
    Date: July 15, 1998

    Meeting with Prince Andrew at Little St. James Island on 07/20/1998.
    Flight departing TEB at 3pm, arriving TIST at 7pm.

    Ghislaine Maxwell will join us for dinner. Bill Clinton may visit
    next week (around July 28, 1998).

    The property was purchased in 1998. Legal proceedings began on
    March 12, 2008 when the lawsuit was filed in Palm Beach.

    Deposition scheduled for 2019-08-15.
    """

    # Mock entities (would come from EntityExtractor)
    entities = {
        'persons': [
            {'text': 'Jeffrey Epstein', 'count': 2, 'confidence': 0.95},
            {'text': 'Prince Andrew', 'count': 1, 'confidence': 0.92},
            {'text': 'Ghislaine Maxwell', 'count': 1, 'confidence': 0.94},
            {'text': 'Bill Clinton', 'count': 1, 'confidence': 0.91},
        ],
        'locations': [
            {'text': 'Little St. James Island', 'count': 1, 'confidence': 0.98},
            {'text': 'Palm Beach', 'count': 1, 'confidence': 0.95},
        ],
    }

    # Mock metadata
    metadata = {
        'pdf_metadata': {
            'creation_date': '1998-07-15T10:30:00',
        }
    }

    events = builder.extract_timeline_events(
        text=test_text,
        entities=entities,
        metadata=metadata,
        doc_id="test_doc_001"
    )

    print(f"Extracted {len(events)} timeline events:")
    print("-" * 70)

    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event['date']} (confidence: {event['date_confidence']})")
        print(f"   Type: {event['event_type']}")
        print(f"   Description: {event['description']}")
        if event['participants']:
            print(f"   Participants: {', '.join(event['participants'])}")
        if event['locations']:
            print(f"   Locations: {', '.join(event['locations'])}")
        print(f"   Context: {event['context_snippet'][:80]}...")

    # Test serialization
    print("\n" + "=" * 70)
    print("Testing serialization...")
    json_str = builder.serialize_events(events)
    print(f"✓ Serialized to {len(json_str)} chars")

    deserialized = builder.deserialize_events(json_str)
    print(f"✓ Deserialized {len(deserialized)} events")
