"""
Hugging Face dataset client for storing and retrieving analysis results.

This is the interface layer between our processing system and the HF dataset.
Only analysis results are stored - NEVER source documents.
"""
import logging
from typing import Dict, List, Optional, Any
from datasets import load_dataset, Dataset, DatasetDict
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
        Load all tables from HF Hub.

        Args:
            split: Specific split to load (default: 'train')

        Returns:
            DatasetDict containing all tables
        """
        logger.info(f"Loading dataset from HF Hub: {self.repo}")
        try:
            # We need to load each configuration (table) separately
            tables = {}
            for table_name in HFConfig.get_all_features().keys():
                try:
                    logger.debug(f"Loading table: {table_name}")
                    ds = load_dataset(
                        self.repo,
                        table_name, # Config name
                        split=split or "train",
                        token=self.token
                    )
                    tables[table_name] = ds
                except Exception as e:
                    logger.warning(f"Could not load table {table_name}: {e}")
                    # Initialize empty if missing/empty
                    logger.info(f"Initializing empty table in memory: {table_name}")
                    features = HFConfig.get_all_features()[table_name]
                    # Create empty dataset with schema
                    data = {k: [] for k in features.keys()}
                    tables[table_name] = Dataset.from_dict(data, features=features)

            self.dataset = DatasetDict(tables)
            logger.info(f"✓ Dataset loaded successfully ({len(tables)} tables)")
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
            # Load current dataset if needed
            if not self.dataset:
                self.load_dataset()

            table_name = 'document_analyses'
            if table_name not in self.dataset:
                logger.error(f"Table {table_name} not found in dataset")
                return False

            current_table = self.dataset[table_name]

            # Convert dict to single-row dataset
            # Ensure values are lists
            data = {k: [v] for k, v in analysis.items()}
            new_row = Dataset.from_dict(data, features=HFConfig.get_document_analyses_features())

            # Concatenate
            updated_table = Dataset.from_dict({
                **{k: list(current_table[k]) + list(new_row[k])
                   for k in current_table.column_names}
            }, features=HFConfig.get_document_analyses_features()) # Explicit features to ensure schema

            # Update local state
            self.dataset[table_name] = updated_table

            # Push to hub (just this config)
            self._push_table(table_name, updated_table)

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

            table_name = 'session_checkpoints'
            current_table = self.dataset[table_name]

            data = {k: [v] for k, v in checkpoint.items()}
            new_row = Dataset.from_dict(data, features=HFConfig.get_session_checkpoints_features())

            updated_table = Dataset.from_dict({
                **{k: list(current_table[k]) + list(new_row[k])
                   for k in current_table.column_names}
            }, features=HFConfig.get_session_checkpoints_features())

            self.dataset[table_name] = updated_table
            self._push_table(table_name, updated_table)

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

            if 'session_checkpoints' not in self.dataset:
                return None

            checkpoints = self.dataset['session_checkpoints']

            if len(checkpoints) == 0:
                return None

            # Return last checkpoint as dict
            latest = checkpoints[-1]
            return {k: latest[k] for k in checkpoints.column_names}

        except Exception as e:
            logger.error(f"Failed to get latest checkpoint: {e}")
            return None

    # ... (Query methods omitted for brevity as they are read-only and similar logic) ...
    # Re-implementing them briefly to ensure file integrity

    def get_total_documents_processed(self) -> int:
        """
        Get total number of documents processed.

        Returns:
            Count of documents in document_analyses table
        """
        try:
            if not self.dataset:
                self.load_dataset()

            if 'document_analyses' in self.dataset:
                return len(self.dataset['document_analyses'])
            return 0

        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0

    def _push_table(self, table_name: str, dataset: Dataset):
        """Push a specific table (config) to HF Hub."""
        try:
            dataset.push_to_hub(
                self.repo,
                config_name=table_name,
                split="train",
                private=HFConfig.PRIVATE,
                token=self.token
            )
            logger.debug(f"Table {table_name} pushed to HF Hub")
        except Exception as e:
            logger.error(f"Failed to push {table_name} to HF Hub: {e}")
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
