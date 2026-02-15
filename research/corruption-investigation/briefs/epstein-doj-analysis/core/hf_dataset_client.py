"""
Hugging Face dataset client for storing and retrieving analysis results.

This is the interface layer between our processing system and the HF dataset.
Only analysis results are stored - NEVER source documents.
"""
import logging
from typing import Dict, List, Optional, Any
from datasets import load_dataset, Dataset
from huggingface_hub import HfApi
from config.hf_config import HFConfig

logger = logging.getLogger(__name__)


class HFDatasetClient:
    """
    Client for interacting with Hugging Face dataset.

    Stores ONLY analysis results, never source documents.
    """

    def __init__(self, repo: str = None, token: str = None):
        """
        Initialize HF dataset client.

        Args:
            repo: HF repository name (default from config)
            token: HF authentication token (default from config)
        """
        self.repo = repo or HFConfig.DEFAULT_REPO
        self.token = token or HFConfig.HF_TOKEN

        if not self.token:
            raise ValueError(
                "HF_TOKEN required. Set in environment or pass to constructor."
            )

        self.dataset = None
        self.api = HfApi()
        logger.info(f"HF Dataset Client initialized for: {self.repo}")

    def load_dataset(self, split: str = None) -> Any:
        """
        Load dataset from HF Hub.

        Args:
            split: Specific split/table to load (default: load all)

        Returns:
            Dataset or DatasetDict
        """
        logger.info(f"Loading dataset from HF Hub: {self.repo}")
        try:
            if split:
                self.dataset = load_dataset(
                    self.repo,
                    split=split,
                    token=self.token
                )
            else:
                self.dataset = load_dataset(
                    self.repo,
                    token=self.token
                )
            logger.info("✓ Dataset loaded successfully")
            return self.dataset
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    def add_document_analysis(self, analysis: Dict) -> bool:
        """
        Add document analysis result to dataset.

        Args:
            analysis: Analysis dictionary matching document_analyses schema

        Returns:
            True if successful
        """
        try:
            # Load current dataset
            if not self.dataset:
                self.load_dataset()

            # Add to document_analyses table
            current_table = self.dataset['document_analyses']

            # Convert dict to single-row dataset
            new_row = Dataset.from_dict({k: [v] for k, v in analysis.items()})

            # Concatenate
            updated_table = Dataset.from_dict({
                **{k: list(current_table[k]) + list(new_row[k])
                   for k in current_table.column_names}
            })

            # Update dataset dict
            self.dataset['document_analyses'] = updated_table

            # Push to hub
            self._push_to_hub()

            logger.info(f"✓ Added analysis for doc: {analysis.get('doc_id')}")
            return True

        except Exception as e:
            logger.error(f"Failed to add document analysis: {e}")
            return False

    def add_checkpoint(self, checkpoint: Dict) -> bool:
        """
        Add session checkpoint.

        Args:
            checkpoint: Checkpoint dictionary matching session_checkpoints schema

        Returns:
            True if successful
        """
        try:
            if not self.dataset:
                self.load_dataset()

            current_table = self.dataset['session_checkpoints']
            new_row = Dataset.from_dict({k: [v] for k, v in checkpoint.items()})

            updated_table = Dataset.from_dict({
                **{k: list(current_table[k]) + list(new_row[k])
                   for k in current_table.column_names}
            })

            self.dataset['session_checkpoints'] = updated_table
            self._push_to_hub()

            logger.info(f"✓ Added checkpoint: {checkpoint.get('session_id')}")
            return True

        except Exception as e:
            logger.error(f"Failed to add checkpoint: {e}")
            return False

    def get_latest_checkpoint(self) -> Optional[Dict]:
        """
        Get the most recent session checkpoint.

        Returns:
            Latest checkpoint dict or None if no checkpoints exist
        """
        try:
            if not self.dataset:
                self.load_dataset()

            checkpoints = self.dataset['session_checkpoints']

            if len(checkpoints) == 0:
                return None

            # Return last checkpoint as dict
            latest = checkpoints[-1]
            return {k: latest[k] for k in checkpoints.column_names}

        except Exception as e:
            logger.error(f"Failed to get latest checkpoint: {e}")
            return None

    def query_entities(self, entity_name: str = None, entity_type: str = None) -> List[Dict]:
        """
        Query entity index.

        Args:
            entity_name: Filter by entity name (optional)
            entity_type: Filter by entity type (optional)

        Returns:
            List of matching entity records
        """
        try:
            if not self.dataset:
                self.load_dataset()

            entities = self.dataset['entity_index']

            results = []
            for i in range(len(entities)):
                entity = {k: entities[k][i] for k in entities.column_names}

                # Apply filters
                if entity_name and entity['entity_name'] != entity_name:
                    continue
                if entity_type and entity['entity_type'] != entity_type:
                    continue

                results.append(entity)

            return results

        except Exception as e:
            logger.error(f"Failed to query entities: {e}")
            return []

    def get_timeline(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get timeline events, optionally filtered by date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of timeline events
        """
        try:
            if not self.dataset:
                self.load_dataset()

            timeline = self.dataset['timeline_master']

            results = []
            for i in range(len(timeline)):
                event = {k: timeline[k][i] for k in timeline.column_names}

                # Apply date filters
                event_date = event['event_date']
                if start_date and event_date < start_date:
                    continue
                if end_date and event_date > end_date:
                    continue

                results.append(event)

            # Sort by date
            results.sort(key=lambda x: x['event_date'])

            return results

        except Exception as e:
            logger.error(f"Failed to get timeline: {e}")
            return []

    def get_total_documents_processed(self) -> int:
        """
        Get total number of documents processed.

        Returns:
            Count of documents in document_analyses table
        """
        try:
            if not self.dataset:
                self.load_dataset()

            return len(self.dataset['document_analyses'])

        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0

    def _push_to_hub(self):
        """Push updated dataset to HF Hub."""
        try:
            self.dataset.push_to_hub(
                self.repo,
                private=HFConfig.PRIVATE,
                token=self.token
            )
            logger.debug("Dataset pushed to HF Hub")
        except Exception as e:
            logger.error(f"Failed to push to HF Hub: {e}")
            raise


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    print("Testing HF Dataset Client...")

    try:
        client = HFDatasetClient()
        print("✓ Client initialized")

        # Try to load dataset
        dataset = client.load_dataset()
        print(f"✓ Dataset loaded: {len(dataset)} tables")

        # Get stats
        total_docs = client.get_total_documents_processed()
        print(f"✓ Total documents processed: {total_docs}")

        latest_checkpoint = client.get_latest_checkpoint()
        if latest_checkpoint:
            print(f"✓ Latest checkpoint: {latest_checkpoint['session_id']}")
        else:
            print("  No checkpoints yet")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: Run init_hf_dataset.py first to create the dataset")
