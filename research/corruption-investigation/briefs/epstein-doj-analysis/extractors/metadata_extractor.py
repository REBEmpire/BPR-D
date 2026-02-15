"""
Metadata extraction from documents.

Extracts:
- PDF metadata (creation date, author, producer)
- Bates numbers
- Case numbers
- Filing dates
- Court information
- Email headers
- Location references
"""
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pypdf import PdfReader
import io

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract metadata from documents."""

    def __init__(self):
        """Initialize metadata extractor."""
        # Regex patterns for common metadata
        self.patterns = {
            'bates': [
                r'[A-Z]+[-\s]?\d{3,}',  # e.g., EPSTEIN-001, GX 123
                r'Bates\s+(?:No\.?|Number)?\s*([A-Z0-9\-]+)',
            ],
            'case_number': [
                r'\d{2,4}[-\s]cv[-\s]\d{4,}',  # Civil case format
                r'\d{2,4}[-\s]cr[-\s]\d{4,}',  # Criminal case format
                r'Case\s+No\.?\s*([0-9:\-]+)',
            ],
            'docket': [
                r'Doc(?:ument)?[\s#]+\d+',
                r'Docket\s+(?:No\.?|Number)?\s*#?\s*\d+',
            ],
            'date': [
                r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
            ],
            'flight_log': [
                r'N\d{3,5}[A-Z]{1,2}',  # Aircraft registration
                r'[A-Z]{3,4}\s+to\s+[A-Z]{3,4}',  # Airport codes
            ],
            'email': [
                r'From:\s+(.+?)(?:\n|$)',
                r'To:\s+(.+?)(?:\n|$)',
                r'Subject:\s+(.+?)(?:\n|$)',
                r'Date:\s+(.+?)(?:\n|$)',
            ],
        }

    def extract_pdf_metadata(self, pdf_stream: io.BytesIO) -> Dict:
        """
        Extract PDF-level metadata.

        Args:
            pdf_stream: PDF file as BytesIO object

        Returns:
            Dictionary with PDF metadata
        """
        metadata = {
            'title': None,
            'author': None,
            'subject': None,
            'creator': None,
            'producer': None,
            'creation_date': None,
            'modification_date': None,
            'page_count': 0,
        }

        try:
            pdf_stream.seek(0)  # Reset to start
            reader = PdfReader(pdf_stream)

            # Basic metadata
            if reader.metadata:
                meta = reader.metadata
                metadata['title'] = meta.title if hasattr(meta, 'title') else None
                metadata['author'] = meta.author if hasattr(meta, 'author') else None
                metadata['subject'] = meta.subject if hasattr(meta, 'subject') else None
                metadata['creator'] = meta.creator if hasattr(meta, 'creator') else None
                metadata['producer'] = meta.producer if hasattr(meta, 'producer') else None

                # Dates
                if hasattr(meta, 'creation_date') and meta.creation_date:
                    metadata['creation_date'] = self._parse_pdf_date(meta.creation_date)
                if hasattr(meta, 'modification_date') and meta.modification_date:
                    metadata['modification_date'] = self._parse_pdf_date(meta.modification_date)

            # Page count
            metadata['page_count'] = len(reader.pages)

            logger.debug(f"Extracted PDF metadata: {metadata['page_count']} pages")

        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")

        return metadata

    def extract_bates_numbers(self, text: str) -> List[str]:
        """
        Extract Bates numbers from text.

        Args:
            text: Document text

        Returns:
            List of Bates numbers found
        """
        bates_numbers = []

        for pattern in self.patterns['bates']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            bates_numbers.extend(matches)

        # Deduplicate and clean
        bates_numbers = list(set([b.strip() for b in bates_numbers if b.strip()]))

        logger.debug(f"Found {len(bates_numbers)} Bates numbers")

        return bates_numbers

    def extract_case_numbers(self, text: str) -> List[str]:
        """
        Extract case numbers from text.

        Args:
            text: Document text

        Returns:
            List of case numbers found
        """
        case_numbers = []

        for pattern in self.patterns['case_number']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches and isinstance(matches[0], tuple):
                # Pattern had capture group
                case_numbers.extend([m[0] if isinstance(m, tuple) else m for m in matches])
            else:
                case_numbers.extend(matches)

        # Clean and deduplicate
        case_numbers = list(set([c.strip() for c in case_numbers if c and c.strip()]))

        logger.debug(f"Found {len(case_numbers)} case numbers")

        return case_numbers

    def extract_all_metadata(self, pdf_stream: io.BytesIO, text: str) -> Dict:
        """
        Extract all metadata from document.

        Args:
            pdf_stream: PDF file as BytesIO
            text: Extracted document text

        Returns:
            Complete metadata dictionary
        """
        metadata = {
            'pdf_metadata': self.extract_pdf_metadata(pdf_stream),
            'bates_numbers': self.extract_bates_numbers(text),
            'case_numbers': self.extract_case_numbers(text),
            'document_type': self._classify_document_type(text),
        }

        logger.info(
            f"Metadata extraction complete: "
            f"{len(metadata['bates_numbers'])} Bates, "
            f"{len(metadata['case_numbers'])} cases, "
            f"type: {metadata['document_type']}"
        )

        return metadata

    def _classify_document_type(self, text: str) -> str:
        """Classify document type based on content."""
        text_lower = text.lower()[:1000]

        if 'from:' in text_lower and 'subject:' in text_lower:
            return 'email'
        elif any(term in text_lower for term in ['plaintiff', 'defendant', 'court', 'motion']):
            return 'court_filing'
        elif 'fbi' in text_lower:
            return 'fbi_file'
        elif 'flight' in text_lower:
            return 'flight_log'
        else:
            return 'unknown'

    def _parse_pdf_date(self, pdf_date) -> Optional[str]:
        """Parse PDF date to ISO format string."""
        try:
            if isinstance(pdf_date, datetime):
                return pdf_date.isoformat()
            else:
                return str(pdf_date)
        except:
            return None
