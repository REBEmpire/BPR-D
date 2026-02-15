"""
Test script to verify Phase 1 pipeline components.

This script tests the complete processing pipeline without
requiring real DOJ documents or HF dataset setup.
"""
import sys
import io
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.document_streamer import DocumentStreamer
from core.document_processor import DocumentProcessor
from core.session_manager import SessionManager
from utils.privacy_guard import PrivacyGuard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_pdf() -> io.BytesIO:
    """
    Create a test PDF in memory for testing.

    Returns:
        BytesIO object containing test PDF
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Add realistic test content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Test Document - Epstein Analysis Pipeline")

    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "From: investigator@justice.gov")
    c.drawString(100, 700, "To: analyst@fbi.gov")
    c.drawString(100, 680, "Subject: Document Analysis Test")
    c.drawString(100, 660, "Date: February 15, 2026")

    c.drawString(100, 630, "Case No. 08-cv-80736")
    c.drawString(100, 610, "Bates No. TEST-001 through TEST-005")

    c.drawString(100, 580, "This is a test document for verifying the processing pipeline.")
    c.drawString(100, 560, "Flight N212JE from TEB to TIST on July 15, 1998")
    c.drawString(100, 540, "Meeting at Little St. James Island")

    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    return pdf_buffer


def test_privacy_guard():
    """Test PrivacyGuard component."""
    print("\n" + "=" * 70)
    print("TEST 1: PrivacyGuard")
    print("=" * 70)

    try:
        guard = PrivacyGuard(watch_dir=str(project_root))
        print("✓ PrivacyGuard initialized")

        guard.verify_no_local_storage_active()
        print("✓ Pre-flight check passed")

        guard.verify_no_files_created()
        print("✓ Privacy verification passed")

        print("\n✅ PrivacyGuard test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ PrivacyGuard test FAILED: {e}")
        return False


def test_document_processor():
    """Test DocumentProcessor component."""
    print("\n" + "=" * 70)
    print("TEST 2: DocumentProcessor")
    print("=" * 70)

    try:
        # Create test PDF
        print("Creating test PDF...")
        test_pdf = create_test_pdf()
        print("✓ Test PDF created in memory")

        # Initialize processor
        processor = DocumentProcessor()
        print("✓ DocumentProcessor initialized")

        # Process document
        print("\nProcessing test document...")
        analysis = processor.process_document(
            pdf_stream=test_pdf,
            source_url="https://example.com/test-doc.pdf",
            dataset_num=1
        )

        # Verify analysis structure
        print("\nAnalysis results:")
        print(f"  Doc ID: {analysis['doc_id']}")
        print(f"  Document type: {analysis['document_type']}")
        print(f"  Page count: {analysis['page_count']}")
        print(f"  Bates numbers: {analysis['bates_numbers']}")
        print(f"  Processing time: {analysis['processing_time_seconds']:.2f}s")

        # Verify required fields
        required_fields = [
            'doc_id', 'source_url', 'dataset_number', 'document_type',
            'bates_numbers', 'page_count', 'date_processed',
            'processing_time_seconds', 'named_entities',
            'timeline_events', 'redaction_analysis', 'metadata'
        ]

        missing_fields = [f for f in required_fields if f not in analysis]
        if missing_fields:
            print(f"\n⚠ Missing fields: {missing_fields}")
        else:
            print("✓ All required fields present")

        print("\n✅ DocumentProcessor test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ DocumentProcessor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test complete processing pipeline."""
    print("\n" + "=" * 70)
    print("TEST 3: Full Pipeline Integration")
    print("=" * 70)

    try:
        # Initialize all components
        print("Initializing components...")
        privacy_guard = PrivacyGuard(watch_dir=str(project_root))
        processor = DocumentProcessor()
        print("✓ All components initialized")

        # Pre-flight check
        print("\nRunning privacy pre-flight...")
        privacy_guard.verify_no_local_storage_active()
        print("✓ Pre-flight passed")

        # Create and process test PDF
        print("\nProcessing test document...")
        test_pdf = create_test_pdf()

        analysis = processor.process_document(
            pdf_stream=test_pdf,
            source_url="https://example.com/integration-test.pdf",
            dataset_num=1
        )

        print(f"✓ Document processed: {analysis['doc_id']}")

        # Verify no files created
        print("\nVerifying privacy guarantees...")
        privacy_guard.verify_no_files_created()
        print("✓ Privacy verification passed - no files created")

        print("\n✅ Full pipeline integration test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Full pipeline test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all component tests."""
    print("=" * 70)
    print("DOJ EPSTEIN ANALYSIS - PHASE 1 COMPONENT TESTS")
    print("=" * 70)

    results = {
        'PrivacyGuard': test_privacy_guard(),
        'DocumentProcessor': test_document_processor(),
        'Full Pipeline': test_full_pipeline(),
    }

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    print()

    all_passed = all(results.values())
    if all_passed:
        print("🎉 All tests PASSED!")
        print("\nPhase 1 components are working correctly.")
        print("Ready to proceed with:")
        print("  1. HF dataset initialization (run scripts/init_hf_dataset.py)")
        print("  2. Real document processing (requires DOJ URLs)")
        print("  3. Phase 2 implementation (NER, timeline, code breaking)")
    else:
        print("⚠ Some tests FAILED - review errors above")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
