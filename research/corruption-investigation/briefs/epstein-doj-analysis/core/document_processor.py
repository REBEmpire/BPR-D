"""
Main document processing pipeline.

Coordinates all components to process documents from PDF stream
to structured analysis results.
"""
import io
import json
import logging
import time
from typing import Dict
from datetime import datetime
from pathlib import Path
import sys
import hashlib

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pdfplumber
from extractors.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Main processing pipeline that coordinates document analysis.

    This is the heart of Phase 1 - it takes a PDF stream and returns
    structured analysis data ready for HF dataset storage.
    """

    def __init__(self):
        """Initialize document processor."""
        self.metadata_extractor = MetadataExtractor()
        logger.info("DocumentProcessor initialized")

    def process_document(
        self,
        pdf_stream: io.BytesIO,
        source_url: str,
        dataset_num: int
    ) -> Dict:
        """
        Process a single document end-to-end.

        Args:
            pdf_stream: PDF file as BytesIO object (in-memory)
            source_url: Original URL of the document
            dataset_num: Dataset number (1-12)

        Returns:
            Dictionary with complete analysis matching HF schema

        Raises:
            Exception: If processing fails
        """
        start_time = time.time()
        logger.info(f"Processing document from: {source_url}")

        try:
            # 1. Extract text
            text = self._extract_text(pdf_stream)
            logger.debug(f"Extracted {len(text)} characters of text")

            # 2. Extract metadata
            metadata = self.metadata_extractor.extract_all_metadata(pdf_stream, text)

            # 3. Generate unique doc_id
            doc_id = self._generate_doc_id(dataset_num, source_url)

            # 4. Calculate processing time
            processing_time = time.time() - start_time

            # 5. Build analysis dict (matches HF schema)
            analysis = {
                'doc_id': doc_id,
                'source_url': source_url,
                'dataset_number': dataset_num,
                'document_type': metadata['document_type'],
                'bates_numbers': metadata['bates_numbers'],
                'page_count': metadata['pdf_metadata']['page_count'],
                'date_processed': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,

                # Phase 2 components (placeholders for now)
                'named_entities': '{}',  # Will be populated by EntityExtractor
                'timeline_events': '[]',  # Will be populated by TimelineBuilder
                'redaction_analysis': '{}',  # Will be populated by RedactionDetector

                # Full metadata as JSON
                'metadata': json.dumps(metadata),
            }

            logger.info(
                f"✓ Document processed: {doc_id} "
                f"({metadata['document_type']}, "
                f"{metadata['pdf_metadata']['page_count']} pages, "
                f"{processing_time:.1f}s)"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error processing document {source_url}: {e}", exc_info=True)
            raise

    def _extract_text(self, pdf_stream: io.BytesIO) -> str:
        """
        Extract text from PDF using pdfplumber.

        Args:
            pdf_stream: PDF as BytesIO object

        Returns:
            Extracted text content
        """
        text_parts = []

        try:
            pdf_stream.seek(0)  # Reset to start

            with pdfplumber.open(pdf_stream) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")
                        # Continue with other pages

            full_text = '\n\n'.join(text_parts)

            if not full_text.strip():
                logger.warning("No text extracted - document may be scanned/image-based")
                # TODO: In Phase 2, trigger OCR here

            return full_text

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    def _generate_doc_id(self, dataset_num: int, source_url: str) -> str:
        """
        Generate unique document ID.

        Uses hash of URL to ensure uniqueness and reproducibility.

        Args:
            dataset_num: Dataset number (1-12)
            source_url: Document URL

        Returns:
            Document ID string (e.g., "dataset_1_doc_a3f2b9")
        """
        # Create hash of URL for uniqueness
        url_hash = hashlib.md5(source_url.encode()).hexdigest()[:6]

        doc_id = f"dataset_{dataset_num}_doc_{url_hash}"

        return doc_id


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    print("Testing DocumentProcessor...")

    processor = DocumentProcessor()
    print("✓ Processor initialized")

    # Create a minimal test PDF in memory
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    # Generate test PDF
    test_pdf_buffer = io.BytesIO()
    c = canvas.Canvas(test_pdf_buffer, pagesize=letter)
    c.drawString(100, 750, "Test Document")
    c.drawString(100, 730, "From: test@example.com")
    c.drawString(100, 710, "Subject: Test Email")
    c.drawString(100, 690, "Bates No. TEST-001")
    c.drawString(100, 670, "Case No. 08-cv-12345")
    c.showPage()
    c.save()

    test_pdf_buffer.seek(0)

    # Process test PDF
    try:
        analysis = processor.process_document(
            pdf_stream=test_pdf_buffer,
            source_url="https://example.com/test.pdf",
            dataset_num=1
        )

        print("\n✓ Document processed successfully!")
        print(f"  Doc ID: {analysis['doc_id']}")
        print(f"  Type: {analysis['document_type']}")
        print(f"  Pages: {analysis['page_count']}")
        print(f"  Bates: {analysis['bates_numbers']}")
        print(f"  Cases: {json.loads(analysis['metadata'])['case_numbers']}")
        print(f"  Processing time: {analysis['processing_time_seconds']:.2f}s")

    except Exception as e:
        print(f"✗ Error: {e}")
