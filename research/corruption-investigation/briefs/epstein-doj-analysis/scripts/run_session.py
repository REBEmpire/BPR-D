"""
Main entry point for document processing sessions.

Coordinates all components for time-boxed (60min default) document analysis.
"""
import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.document_streamer import DocumentStreamer
from core.document_processor import DocumentProcessor
from core.session_manager import SessionManager
from core.hf_dataset_client import HFDatasetClient
from utils.privacy_guard import PrivacyGuard
from analyzers.cross_document_coordinator import CrossDocumentCoordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_sample_urls(count=3):
    """
    Get sample document URLs for testing.

    NOTE: This is a placeholder. In production, this would fetch
    real URLs from the DOJ website index.

    Args:
        count: Number of URLs to return

    Returns:
        List of document URLs
    """
    logger.warning("Using placeholder URLs - real DOJ URL fetching not yet implemented")

    # Placeholder URLs for testing
    # In production, these would be real DOJ document URLs
    return [
        f"https://example.com/sample-doc-{i}.pdf"
        for i in range(count)
    ]


def run_processing_session(
    time_budget_minutes: int = 60,
    resume: bool = True,
    test_mode: bool = False
):
    """
    Execute a time-boxed document processing session.

    Args:
        time_budget_minutes: Total session time budget (default 60min)
        resume: Resume from last checkpoint if True (default True)
        test_mode: Use test mode (skip real processing) if True
    """
    print("=" * 70)
    print("DOJ EPSTEIN DOCUMENT ANALYSIS - PROCESSING SESSION")
    print("Research Focus Project #1")
    print("=" * 70)
    print()

    # Initialize components
    logger.info("Initializing components...")

    privacy_guard = PrivacyGuard(watch_dir=str(project_root))
    session_mgr = SessionManager()
    doc_streamer = DocumentStreamer()
    doc_processor = DocumentProcessor(phase2_enabled=True)  # Enable Phase 2 analysis
    hf_client = HFDatasetClient()
    cross_doc_coordinator = CrossDocumentCoordinator(batch_size=10)  # Process batch every 10 docs

    print("✓ All components initialized (Phase 2 analysis enabled)")
    print()

    # Privacy pre-flight check
    print("Running privacy pre-flight check...")
    privacy_guard.verify_no_local_storage_active()
    print("✓ Privacy check passed")
    print()

    # Resume or create new session
    session_id = None
    current_dataset = 1
    current_doc_index = 0

    if resume:
        print("Attempting to resume from last checkpoint...")
        state = session_mgr.resume_session()

        if state:
            session_id = state['session_id']
            current_dataset = state['dataset_num']
            current_doc_index = state['doc_index']
            print(f"✓ Resumed session: {session_id}")
            print(f"  Dataset {current_dataset}, Document index {current_doc_index}")
            print(f"  Total processed: {state['total_processed']} documents")
        else:
            print("  No previous session found")
            session_id = session_mgr.create_session(dataset_num=1, doc_index=0)
            print(f"✓ Created new session: {session_id}")
    else:
        session_id = session_mgr.create_session(dataset_num=1, doc_index=0)
        print(f"✓ Created new session: {session_id}")

    print()

    # Get document URLs
    # TODO: Replace with real DOJ URL fetching
    if test_mode:
        print("⚠ TEST MODE - Using sample URLs (no real documents will be processed)")
        doc_urls = get_sample_urls(count=2)
    else:
        doc_urls = get_sample_urls(count=5)

    print(f"Document queue: {len(doc_urls)} documents")
    print()

    # Processing loop
    docs_processed = 0
    start_time = time.time()
    end_time = start_time + (time_budget_minutes * 60) - 300  # 5min buffer for wrap-up

    print(f"Starting processing (budget: {time_budget_minutes} minutes)...")
    print("-" * 70)

    for i, doc_url in enumerate(doc_urls, start=1):
        # Check time budget
        remaining_time = end_time - time.time()
        if remaining_time < 600:  # Less than 10min remaining
            print(f"\n⏱ Less than 10min remaining, wrapping up session...")
            break

        print(f"\n[{i}/{len(doc_urls)}] Processing: {doc_url}")

        try:
            # In test mode, skip actual processing
            if test_mode:
                print("  [TEST MODE] Skipping actual document processing")
                time.sleep(1)  # Simulate processing time
                docs_processed += 1
                current_doc_index += 1
                continue

            # Stream PDF (in-memory only)
            # NOTE: This will fail with placeholder URLs - that's expected
            # In real use, these would be valid DOJ PDF URLs
            pdf_stream = doc_streamer.stream_pdf(doc_url)

            # Process document
            analysis = doc_processor.process_document(
                pdf_stream=pdf_stream,
                source_url=doc_url,
                dataset_num=current_dataset
            )

            # Save to HF dataset
            success = hf_client.add_document_analysis(analysis)

            if success:
                print(f"  ✓ Analysis saved to HF dataset")
                docs_processed += 1
                current_doc_index += 1

                # Add to cross-document coordinator (Phase 2)
                if analysis.get('_phase2_results'):
                    phase2 = analysis['_phase2_results']

                    batch_ready = cross_doc_coordinator.add_document_results(
                        doc_id=analysis['doc_id'],
                        entities=phase2['entities'],
                        network=phase2['network'],
                        timeline_events=phase2['timeline_events'],
                        code_analysis=phase2['code_analysis'],
                        location_analysis=phase2['location_analysis']
                    )

                    # Process batch if ready
                    if batch_ready:
                        print(f"\n  🔄 Processing cross-document batch...")
                        batch_results = cross_doc_coordinator.process_batch()

                        # TODO: Save batch results to HF dataset
                        # - entity_index table
                        # - network_relationships table
                        # - timeline_master table
                        # - code_dictionary table
                        # - location_activities table

                        print(f"  ✓ Batch processed: {batch_results['batch_metadata']['documents_processed']} docs correlated")

            else:
                print(f"  ✗ Failed to save to HF dataset")

            # Checkpoint every 5 documents
            if docs_processed % 5 == 0:
                session_mgr.update_checkpoint(
                    session_id=session_id,
                    dataset_num=current_dataset,
                    doc_index=current_doc_index,
                    docs_processed=docs_processed
                )
                print(f"  💾 Checkpoint saved ({docs_processed} documents)")

        except Exception as e:
            logger.error(f"Error processing {doc_url}: {e}")
            print(f"  ✗ Error: {e}")
            continue

    # Session wrap-up
    print()
    print("-" * 70)
    print("Wrapping up session...")

    # Final checkpoint
    session_mgr.complete_session(session_id)
    print("✓ Final checkpoint saved")

    # Privacy verification
    print("\nRunning final privacy verification...")
    try:
        privacy_guard.verify_no_files_created()
        print("✓ Privacy verification PASSED - No files created")
    except RuntimeError as e:
        print(f"✗ PRIVACY VIOLATION: {e}")
        logger.error(f"Privacy violation detected: {e}")

    # Session summary
    elapsed_time = time.time() - start_time
    elapsed_min = elapsed_time / 60

    print()
    print("=" * 70)
    print("SESSION COMPLETE")
    print("=" * 70)
    print(f"Session ID: {session_id}")
    print(f"Documents processed: {docs_processed}")
    print(f"Time elapsed: {elapsed_min:.1f} minutes")
    if docs_processed > 0:
        print(f"Average time per document: {elapsed_time / docs_processed:.1f} seconds")
    print(f"Dataset position: Dataset {current_dataset}, Doc index {current_doc_index}")
    print("=" * 70)

    # Get overall progress
    total_processed = hf_client.get_total_documents_processed()
    print(f"\nTotal documents processed to date: {total_processed}")
    print()

    return {
        'session_id': session_id,
        'docs_processed': docs_processed,
        'elapsed_minutes': elapsed_min,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run DOJ Epstein document analysis session'
    )
    parser.add_argument(
        '--time',
        type=int,
        default=60,
        help='Session time budget in minutes (default: 60)'
    )
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start new session instead of resuming'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (skip actual processing)'
    )

    args = parser.parse_args()

    try:
        run_processing_session(
            time_budget_minutes=args.time,
            resume=not args.no_resume,
            test_mode=args.test
        )

    except KeyboardInterrupt:
        print("\n\n⚠ Session interrupted by user")
        logger.info("Session interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n✗ Session failed: {e}")
        logger.error(f"Session failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
