"""
Session state management via HF dataset.
Enables resume across multiple work sessions.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.hf_dataset_client import HFDatasetClient

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manage session state with Hugging Face dataset backend.

    Enables daily 60-minute sessions that can pick up exactly where
    they left off, even across multiple days.
    """

    def __init__(self, hf_client: HFDatasetClient = None):
        """
        Initialize session manager.

        Args:
            hf_client: HF dataset client (creates one if not provided)
        """
        self.hf_client = hf_client or HFDatasetClient()
        self.current_session_id = None
        logger.info("Session Manager initialized")

    def create_session(self, dataset_num: int = 1, doc_index: int = 0) -> str:
        """
        Start new session.

        Args:
            dataset_num: Starting dataset number (1-12)
            doc_index: Starting document index within dataset

        Returns:
            New session ID
        """
        # Generate unique session ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        session_id = f"session_{timestamp}_{unique_id}"

        # Get total documents processed so far
        total_processed = self._get_total_processed()

        # Create checkpoint
        checkpoint = {
            'session_id': session_id,
            'date': datetime.now().isoformat(),
            'current_dataset': dataset_num,
            'current_doc_index': doc_index,
            'docs_processed_this_session': 0,
            'total_docs_processed': total_processed,
            'next_url_queue': '[]',  # Empty JSON array
            'session_completed': '',  # Will be filled when session ends
        }

        # Save initial checkpoint
        success = self.hf_client.add_checkpoint(checkpoint)

        if success:
            self.current_session_id = session_id
            logger.info(
                f"Created new session: {session_id} "
                f"(Dataset {dataset_num}, Doc {doc_index})"
            )
            return session_id
        else:
            raise RuntimeError("Failed to create session checkpoint")

    def resume_session(self) -> Optional[Dict]:
        """
        Resume from last checkpoint.

        Returns:
            Dictionary with session state, or None if no checkpoints exist
        """
        latest = self.hf_client.get_latest_checkpoint()

        if not latest:
            logger.info("No previous sessions found")
            return None

        # Check if session was completed
        if latest.get('session_completed'):
            logger.info(
                f"Last session {latest['session_id']} was completed. "
                "Starting fresh session."
            )
            # Start new session from where last one left off
            return self._start_after_completed_session(latest)

        # Resume incomplete session
        self.current_session_id = latest['session_id']
        logger.info(
            f"Resuming session: {latest['session_id']} "
            f"(Dataset {latest['current_dataset']}, "
            f"Doc {latest['current_doc_index']})"
        )

        return {
            'session_id': latest['session_id'],
            'dataset_num': latest['current_dataset'],
            'doc_index': latest['current_doc_index'],
            'total_processed': latest['total_docs_processed'],
            'queue': self._parse_queue(latest['next_url_queue'])
        }

    def update_checkpoint(
        self,
        session_id: str,
        dataset_num: int = None,
        doc_index: int = None,
        docs_processed: int = None,
        url_queue: List[str] = None
    ) -> bool:
        """
        Update current session checkpoint.

        Args:
            session_id: Session ID to update
            dataset_num: Current dataset number (optional)
            doc_index: Current document index (optional)
            docs_processed: Documents processed this session (optional)
            url_queue: Next URL queue (optional)

        Returns:
            True if successful
        """
        # Get current checkpoint
        current = self.hf_client.get_latest_checkpoint()

        if not current or current['session_id'] != session_id:
            logger.error(f"Session {session_id} not found or not current")
            return False

        # Build update dict
        updates = {
            'session_id': session_id,
            'date': current['date'],  # Keep original date
            'current_dataset': dataset_num if dataset_num is not None else current['current_dataset'],
            'current_doc_index': doc_index if doc_index is not None else current['current_doc_index'],
            'docs_processed_this_session': docs_processed if docs_processed is not None else current['docs_processed_this_session'],
            'total_docs_processed': self._get_total_processed(),
            'next_url_queue': self._serialize_queue(url_queue) if url_queue is not None else current['next_url_queue'],
            'session_completed': current.get('session_completed', ''),
        }

        # Add checkpoint
        success = self.hf_client.add_checkpoint(updates)

        if success:
            logger.info(
                f"Updated checkpoint: Dataset {updates['current_dataset']}, "
                f"Doc {updates['current_doc_index']}, "
                f"Processed: {updates['docs_processed_this_session']}"
            )

        return success

    def complete_session(self, session_id: str) -> bool:
        """
        Mark session as completed.

        Args:
            session_id: Session ID to complete

        Returns:
            True if successful
        """
        current = self.hf_client.get_latest_checkpoint()

        if not current or current['session_id'] != session_id:
            logger.error(f"Session {session_id} not found or not current")
            return False

        # Mark as completed
        completed_checkpoint = {
            'session_id': session_id,
            'date': current['date'],
            'current_dataset': current['current_dataset'],
            'current_doc_index': current['current_doc_index'],
            'docs_processed_this_session': current['docs_processed_this_session'],
            'total_docs_processed': self._get_total_processed(),
            'next_url_queue': current['next_url_queue'],
            'session_completed': datetime.now().isoformat(),
        }

        success = self.hf_client.add_checkpoint(completed_checkpoint)

        if success:
            logger.info(
                f"Session {session_id} completed: "
                f"{current['docs_processed_this_session']} documents processed"
            )

        return success

    def get_session_summary(self, session_id: str = None) -> Dict:
        """
        Get summary of session progress.

        Args:
            session_id: Session ID (uses current if not provided)

        Returns:
            Dictionary with session summary
        """
        session_id = session_id or self.current_session_id

        if not session_id:
            return {'error': 'No active session'}

        checkpoint = self.hf_client.get_latest_checkpoint()

        if not checkpoint or checkpoint['session_id'] != session_id:
            return {'error': f'Session {session_id} not found'}

        total_docs = self._get_total_processed()

        return {
            'session_id': session_id,
            'started': checkpoint['date'],
            'current_dataset': checkpoint['current_dataset'],
            'current_doc_index': checkpoint['current_doc_index'],
            'docs_this_session': checkpoint['docs_processed_this_session'],
            'total_docs_processed': total_docs,
            'completed': checkpoint.get('session_completed', None),
            'is_active': not checkpoint.get('session_completed'),
        }

    def _get_total_processed(self) -> int:
        """
        Get total documents processed across all sessions.

        Returns:
            Total document count
        """
        return self.hf_client.get_total_documents_processed()

    def _start_after_completed_session(self, last_checkpoint: Dict) -> Dict:
        """
        Start new session after a completed one.

        Args:
            last_checkpoint: Last completed session checkpoint

        Returns:
            New session state dict
        """
        # Create new session starting from where last one left off
        new_session_id = self.create_session(
            dataset_num=last_checkpoint['current_dataset'],
            doc_index=last_checkpoint['current_doc_index']
        )

        return {
            'session_id': new_session_id,
            'dataset_num': last_checkpoint['current_dataset'],
            'doc_index': last_checkpoint['current_doc_index'],
            'total_processed': self._get_total_processed(),
            'queue': []
        }

    def _serialize_queue(self, queue: List[str]) -> str:
        """
        Serialize URL queue to JSON string.

        Args:
            queue: List of URLs

        Returns:
            JSON string
        """
        import json
        return json.dumps(queue)

    def _parse_queue(self, queue_json: str) -> List[str]:
        """
        Parse URL queue from JSON string.

        Args:
            queue_json: JSON string

        Returns:
            List of URLs
        """
        import json
        try:
            return json.loads(queue_json)
        except:
            return []


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    print("Testing SessionManager...")

    try:
        # Create manager
        manager = SessionManager()
        print("✓ Manager created")

        # Try to resume
        state = manager.resume_session()

        if state:
            print(f"✓ Resumed session: {state['session_id']}")
            print(f"  Dataset: {state['dataset_num']}")
            print(f"  Doc index: {state['doc_index']}")
            print(f"  Total processed: {state['total_processed']}")
        else:
            print("  No previous session - would create new one")
            # session_id = manager.create_session()
            # print(f"✓ Created session: {session_id}")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: Ensure HF dataset is initialized and .env is configured")
