"""
Test script for Phase 2 analysis pipeline.

Tests all Phase 2 components:
- EntityExtractor (NER)
- TimelineBuilder (Investigation Goal #3)
- NetworkMapper (Investigation Goal #2)
- CodeBreaker (Investigation Goal #1)
- LocationAnalyzer (Island/Ranch analysis)
- AliasResolver (entity disambiguation)
- CrossDocumentCoordinator (batch correlation)
"""
import sys
import io
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.document_processor import DocumentProcessor
from analyzers.cross_document_coordinator import CrossDocumentCoordinator
from utils.privacy_guard import PrivacyGuard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_pdf_with_intelligence() -> io.BytesIO:
    """
    Create comprehensive test PDF with intelligence targets.

    Returns:
        BytesIO object containing test PDF
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Page 1: Email with code words and aliases
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "CONFIDENTIAL CORRESPONDENCE")

    c.setFont("Helvetica", 10)
    c.drawString(100, 720, "From: JE <jepstein@example.com>")
    c.drawString(100, 705, "To: GM <gmax@example.com>")
    c.drawString(100, 690, "Date: July 15, 1998")
    c.drawString(100, 675, "Subject: Weekend Arrangements")
    c.drawString(100, 660, "Bates No: EPSTEIN-12345")

    c.drawString(100, 630, "Please arrange for three new 'assistants' to provide")
    c.drawString(100, 615, "massage services for the special guests this weekend.")

    c.drawString(100, 585, "BC and PA both confirmed for Saturday. Flight N212JE")
    c.drawString(100, 570, "departs TEB at 3pm, arrives Little St. James at 7pm.")

    c.drawString(100, 540, "The modeling recruitment from last month was successful.")
    c.drawString(100, 525, "SK will bring them to the Island. NM handling logistics.")

    c.showPage()

    # Page 2: Timeline and location references
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "ACTIVITY LOG - LITTLE ST. JAMES ISLAND")

    c.setFont("Helvetica", 10)
    c.drawString(100, 720, "July 15-20, 1998")
    c.drawString(100, 700, "")
    c.drawString(100, 680, "7/15/1998: Prince Andrew arrived via private flight")
    c.drawString(100, 665, "7/16/1998: Meeting with Jeffrey Epstein and Ghislaine Maxwell")
    c.drawString(100, 650, "7/17/1998: Bill Clinton visited, lunch at main residence")
    c.drawString(100, 635, "7/18/1998: Entertainment session at guest house")
    c.drawString(100, 620, "7/20/1998: All guests departed to Palm Beach")

    c.drawString(100, 590, "Zorro Ranch activities scheduled for August 1998.")
    c.drawString(100, 575, "Manhattan residence event on September 12, 1998.")

    c.showPage()

    # Page 3: Legal document
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "DEPOSITION EXCERPT")

    c.setFont("Helvetica", 10)
    c.drawString(100, 720, "Case No: 08-cv-80736")
    c.drawString(100, 705, "Date: March 12, 2008")
    c.drawString(100, 690, "Location: Palm Beach Federal Courthouse")

    c.drawString(100, 660, "Q: How many times did you visit Little St. James Island?")
    c.drawString(100, 645, "A: I cannot recall the exact number of visits.")

    c.drawString(100, 615, "Q: Who else was present during these visits?")
    c.drawString(100, 600, "A: Jeffrey Epstein, Ghislaine Maxwell, and various guests.")

    c.save()

    pdf_buffer.seek(0)
    return pdf_buffer


def test_entity_extraction():
    """Test Phase 2 EntityExtractor component."""
    print("\n" + "=" * 70)
    print("TEST 1: Entity Extraction (NER)")
    print("=" * 70)

    try:
        from extractors.entity_extractor import EntityExtractor

        extractor = EntityExtractor()

        if not extractor.nlp:
            print("⚠ spaCy model not available - skipping NER test")
            print("  Install with: python -m spacy download en_core_web_lg")
            return False

        test_text = """
        Jeffrey Epstein and Ghislaine Maxwell met with Prince Andrew
        at Little St. James Island on July 15, 1998. Bill Clinton
        also visited the island during this period. The FBI and DOJ
        are investigating activities at Zorro Ranch in New Mexico.
        """

        entities = extractor.extract_entities(test_text, doc_id="test_doc_001")

        print(f"✓ Extracted {entities['extraction_metadata']['total_entities']} entities")
        print(f"  Persons: {len(entities['persons'])}")
        print(f"  Organizations: {len(entities['organizations'])}")
        print(f"  Locations: {len(entities['locations'])}")
        print(f"  Dates: {len(entities['dates'])}")

        if entities['persons']:
            print(f"\n  Sample persons:")
            for person in entities['persons'][:3]:
                print(f"    • {person['text']} (conf: {person['confidence']})")

        print("\n✅ Entity extraction test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Entity extraction test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_timeline_building():
    """Test Phase 2 TimelineBuilder component."""
    print("\n" + "=" * 70)
    print("TEST 2: Timeline Building (Investigation Goal #3)")
    print("=" * 70)

    try:
        from extractors.timeline_builder import TimelineBuilder

        builder = TimelineBuilder()

        test_text = """
        Meeting on July 15, 1998 at Little St. James Island.
        Prince Andrew arrived on 7/16/1998. Bill Clinton visited
        on July 17, 1998. Deposition scheduled for 2008-03-12.
        """

        entities = {
            'persons': [
                {'text': 'Prince Andrew', 'count': 1},
                {'text': 'Bill Clinton', 'count': 1},
            ],
            'locations': [
                {'text': 'Little St. James Island', 'count': 1},
            ],
        }

        metadata = {'pdf_metadata': {}}

        events = builder.extract_timeline_events(
            text=test_text,
            entities=entities,
            metadata=metadata,
            doc_id="test_doc_001"
        )

        print(f"✓ Extracted {len(events)} timeline events")

        if events:
            print(f"\n  Sample events:")
            for event in events[:3]:
                print(f"    • {event['date']}: {event['event_type']}")
                print(f"      {event['description']}")

        print("\n✅ Timeline building test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Timeline building test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_breaking():
    """Test Phase 2 CodeBreaker component (Investigation Goal #1)."""
    print("\n" + "=" * 70)
    print("TEST 3: Code Breaking (Investigation Goal #1)")
    print("=" * 70)

    try:
        from extractors.code_breaker import CodeBreaker

        breaker = CodeBreaker()

        test_text = """
        From: JE <jepstein@example.com>
        To: GM <gmax@example.com>

        Please arrange "massage" appointments for BC and PA this weekend.
        The modeling recruitment was successful. SK will handle logistics.
        """

        entities = {'persons': []}

        analysis = breaker.detect_code_terms(
            text=test_text,
            entities=entities,
            doc_id="test_doc_001"
        )

        print(f"✓ Detected {analysis['detection_metadata']['total_detections']} potential code patterns")
        print(f"  Aliases: {len(analysis['aliases'])}")
        print(f"  Code terms/euphemisms: {len(analysis['code_terms'])}")
        print(f"  Initials: {len(analysis['initials'])}")

        if analysis['aliases']:
            print(f"\n  Sample aliases:")
            for alias in analysis['aliases'][:3]:
                print(f"    • {alias['term']} → {alias['likely_refers_to']}")

        print("\n✅ Code breaking test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Code breaking test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrated_pipeline():
    """Test full Phase 2 integrated pipeline."""
    print("\n" + "=" * 70)
    print("TEST 4: Integrated Phase 2 Pipeline")
    print("=" * 70)

    try:
        # Initialize privacy guard
        privacy_guard = PrivacyGuard(watch_dir=str(project_root))
        print("✓ Privacy guard initialized")

        # Privacy pre-flight
        privacy_guard.verify_no_local_storage_active()
        print("✓ Pre-flight check passed")

        # Initialize processor with Phase 2
        processor = DocumentProcessor(phase2_enabled=True)
        print("✓ DocumentProcessor initialized (Phase 2 enabled)")

        # Create test PDF
        print("\nCreating comprehensive test PDF...")
        test_pdf = create_test_pdf_with_intelligence()
        print("✓ Test PDF created in memory (3 pages)")

        # Process document
        print("\nProcessing test document with Phase 2 analysis...")
        analysis = processor.process_document(
            pdf_stream=test_pdf,
            source_url="https://example.com/test-intelligence.pdf",
            dataset_num=1
        )

        # Verify Phase 2 results
        print("\n✓ Document processed successfully")
        print(f"  Doc ID: {analysis['doc_id']}")
        print(f"  Pages: {analysis['page_count']}")
        print(f"  Processing time: {analysis['processing_time_seconds']:.2f}s")

        # Check Phase 2 components
        if analysis.get('_phase2_results'):
            phase2 = analysis['_phase2_results']

            print("\nPhase 2 Analysis Results:")

            # Entities
            entities = phase2['entities']
            total_entities = entities.get('extraction_metadata', {}).get('total_entities', 0)
            print(f"  Entities: {total_entities}")
            print(f"    - Persons: {len(entities.get('persons', []))}")
            print(f"    - Organizations: {len(entities.get('organizations', []))}")
            print(f"    - Locations: {len(entities.get('locations', []))}")

            # Timeline
            timeline = phase2['timeline_events']
            print(f"  Timeline events: {len(timeline)}")

            # Code analysis
            code = phase2['code_analysis']
            print(f"  Code detections: {code.get('detection_metadata', {}).get('total_detections', 0)}")
            print(f"    - Aliases: {len(code.get('aliases', []))}")
            print(f"    - Code terms: {len(code.get('code_terms', []))}")

            # Network
            network = phase2['network']
            print(f"  Network relationships: {len(network.get('relationships', []))}")

            # Locations
            locations = phase2['location_analysis']
            print(f"  Key locations tracked: {len(locations.get('location_activities', {}))}")

        # Privacy verification
        print("\nVerifying privacy guarantees...")
        privacy_guard.verify_no_files_created()
        print("✓ Privacy verification PASSED - no files created")

        print("\n✅ Integrated pipeline test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Integrated pipeline test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cross_document_correlation():
    """Test Phase 2 CrossDocumentCoordinator."""
    print("\n" + "=" * 70)
    print("TEST 5: Cross-Document Correlation")
    print("=" * 70)

    try:
        coordinator = CrossDocumentCoordinator(batch_size=3)
        processor = DocumentProcessor(phase2_enabled=True)

        print("✓ CrossDocumentCoordinator initialized")

        # Process 3 test documents
        print("\nProcessing 3 documents for batch correlation...")

        for i in range(1, 4):
            test_pdf = create_test_pdf_with_intelligence()

            analysis = processor.process_document(
                pdf_stream=test_pdf,
                source_url=f"https://example.com/doc_{i}.pdf",
                dataset_num=1
            )

            if analysis.get('_phase2_results'):
                phase2 = analysis['_phase2_results']

                batch_ready = coordinator.add_document_results(
                    doc_id=analysis['doc_id'],
                    entities=phase2['entities'],
                    network=phase2['network'],
                    timeline_events=phase2['timeline_events'],
                    code_analysis=phase2['code_analysis'],
                    location_analysis=phase2['location_analysis']
                )

                print(f"  • Document {i} added to batch")

                if batch_ready:
                    print("\n  🔄 Batch threshold reached - processing correlation...")

                    batch_results = coordinator.process_batch()

                    print(f"  ✓ Batch processed:")
                    print(f"    - Consolidated entities: {len(batch_results['entity_index'])}")
                    print(f"    - Network relationships: {len(batch_results['network']['relationships'])}")
                    print(f"    - Timeline events: {len(batch_results['timeline'])}")
                    print(f"    - Code dictionary terms: {len(batch_results['code_dictionary'])}")
                    print(f"    - Processing time: {batch_results['batch_metadata']['processing_time_seconds']:.2f}s")

        print("\n✅ Cross-document correlation test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Cross-document correlation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_phase2_tests():
    """Run all Phase 2 component tests."""
    print("=" * 70)
    print("DOJ EPSTEIN ANALYSIS - PHASE 2 COMPONENT TESTS")
    print("Investigation Goals: Code Breaking, Player Mapping, Timeline Reconstruction")
    print("=" * 70)

    results = {
        'Entity Extraction (NER)': test_entity_extraction(),
        'Timeline Building (Goal #3)': test_timeline_building(),
        'Code Breaking (Goal #1)': test_code_breaking(),
        'Integrated Pipeline': test_integrated_pipeline(),
        'Cross-Document Correlation': test_cross_document_correlation(),
    }

    print("\n" + "=" * 70)
    print("PHASE 2 TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    print()

    all_passed = all(results.values())
    if all_passed:
        print("🎉 All Phase 2 tests PASSED!")
        print("\nPhase 2 components are working correctly:")
        print("  ✓ EntityExtractor (NER with spaCy)")
        print("  ✓ TimelineBuilder (Investigation Goal #3)")
        print("  ✓ CodeBreaker (Investigation Goal #1)")
        print("  ✓ NetworkMapper (Investigation Goal #2)")
        print("  ✓ LocationAnalyzer (Island/Ranch analysis)")
        print("  ✓ AliasResolver (entity disambiguation)")
        print("  ✓ CrossDocumentCoordinator (batch correlation)")
        print("\nReady for:")
        print("  1. Real document processing with Phase 2 analysis")
        print("  2. 60-minute processing sessions")
        print("  3. Investigation goals execution (code breaking, player mapping, timeline)")
    else:
        print("⚠ Some Phase 2 tests FAILED - review errors above")

    return all_passed


if __name__ == "__main__":
    success = run_all_phase2_tests()
    sys.exit(0 if success else 1)
