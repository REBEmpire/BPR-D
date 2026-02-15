"""
Hugging Face dataset configuration.

Defines schema and connection settings for the private HF dataset
that stores analysis results (NOT source documents).
"""
import os
from typing import Optional
from datasets import Features, Value, Sequence
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HFConfig:
    """Hugging Face dataset configuration."""

    # Dataset repository (update with your HF username)
    DEFAULT_REPO = os.getenv('HF_DATASET_REPO', 'your-username/epstein-docs-analysis')

    # Authentication token
    HF_TOKEN = os.getenv('HF_TOKEN', None)

    # Dataset is private by default
    PRIVATE = True

    @staticmethod
    def get_document_analyses_features() -> Features:
        """
        Schema for main document analyses table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'doc_id': Value('string'),
            'source_url': Value('string'),
            'dataset_number': Value('int32'),
            'document_type': Value('string'),
            'bates_numbers': Sequence(Value('string')),
            'page_count': Value('int32'),
            'date_processed': Value('string'),
            'processing_time_seconds': Value('float32'),
            'named_entities': Value('string'),  # JSON string
            'timeline_events': Value('string'),  # JSON string
            'redaction_analysis': Value('string'),  # JSON string
            'metadata': Value('string'),  # JSON string
        })

    @staticmethod
    def get_session_checkpoints_features() -> Features:
        """
        Schema for session checkpoints table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'session_id': Value('string'),
            'date': Value('string'),
            'current_dataset': Value('int32'),
            'current_doc_index': Value('int32'),
            'docs_processed_this_session': Value('int32'),
            'total_docs_processed': Value('int32'),
            'next_url_queue': Value('string'),  # JSON string
            'session_completed': Value('string'),
        })

    @staticmethod
    def get_entity_index_features() -> Features:
        """
        Schema for entity cross-reference table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'entity_name': Value('string'),
            'entity_type': Value('string'),
            'document_ids': Sequence(Value('string')),
            'occurrence_count': Value('int32'),
            'aliases': Sequence(Value('string')),  # Known aliases
        })

    @staticmethod
    def get_timeline_master_features() -> Features:
        """
        Schema for master timeline table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'event_date': Value('string'),
            'event_description': Value('string'),
            'source_doc_ids': Sequence(Value('string')),
            'confidence_score': Value('float32'),
            'location': Value('string'),
            'event_type': Value('string'),
        })

    @staticmethod
    def get_redaction_patterns_features() -> Features:
        """
        Schema for redaction patterns table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'pattern_type': Value('string'),
            'frequency': Value('int32'),
            'document_ids': Sequence(Value('string')),
            'analysis_notes': Value('string'),
        })

    @staticmethod
    def get_code_dictionary_features() -> Features:
        """
        Schema for code names & aliases table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'code_term': Value('string'),
            'likely_refers_to': Value('string'),
            'confidence_score': Value('float32'),
            'source_docs': Sequence(Value('string')),
            'context_snippets': Sequence(Value('string')),
            'pattern_notes': Value('string'),
        })

    @staticmethod
    def get_network_relationships_features() -> Features:
        """
        Schema for network relationships table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'entity_a': Value('string'),
            'entity_b': Value('string'),
            'relationship_type': Value('string'),
            'strength_score': Value('float32'),
            'interaction_count': Value('int32'),
            'interaction_types': Sequence(Value('string')),
            'first_documented': Value('string'),
            'last_documented': Value('string'),
        })

    @staticmethod
    def get_location_activities_features() -> Features:
        """
        Schema for location-specific activities table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'location_name': Value('string'),
            'location_type': Value('string'),
            'activity_date': Value('string'),
            'activity_type': Value('string'),
            'participants': Sequence(Value('string')),
            'description': Value('string'),
            'source_docs': Sequence(Value('string')),
            'related_travel': Sequence(Value('string')),
        })

    @staticmethod
    def get_flight_logs_features() -> Features:
        """
        Schema for flight logs table.

        Returns:
            Features object defining the schema
        """
        return Features({
            'flight_id': Value('string'),
            'aircraft': Value('string'),
            'departure_date': Value('string'),
            'origin': Value('string'),
            'destination': Value('string'),
            'passengers': Sequence(Value('string')),
            'crew': Sequence(Value('string')),
            'related_location_activities': Sequence(Value('string')),
            'source_docs': Sequence(Value('string')),
        })

    @classmethod
    def get_all_features(cls) -> dict:
        """
        Get all table schemas.

        Returns:
            Dictionary mapping table names to Features objects
        """
        return {
            'document_analyses': cls.get_document_analyses_features(),
            'session_checkpoints': cls.get_session_checkpoints_features(),
            'entity_index': cls.get_entity_index_features(),
            'timeline_master': cls.get_timeline_master_features(),
            'redaction_patterns': cls.get_redaction_patterns_features(),
            'code_dictionary': cls.get_code_dictionary_features(),
            'network_relationships': cls.get_network_relationships_features(),
            'location_activities': cls.get_location_activities_features(),
            'flight_logs': cls.get_flight_logs_features(),
        }

    @classmethod
    def validate_token(cls) -> bool:
        """
        Validate that HF token is available.

        Returns:
            True if token is set
        """
        if not cls.HF_TOKEN:
            raise ValueError(
                "HF_TOKEN not found in environment. "
                "Please set it in .env file or environment variables."
            )
        return True
