"""
Document streamer that NEVER writes to disk.
All operations in-memory only.

CRITICAL: This module is the foundation of our privacy guarantee.
NO file I/O operations allowed - all data stays in RAM.
"""
import io
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DocumentStreamer:
    """
    Stream PDFs from DOJ website directly to memory.

    Privacy Guarantee: Zero file I/O operations, all data stays in RAM.
    """

    def __init__(self, timeout: int = 60, user_agent: str = None):
        """
        Initialize document streamer.

        Args:
            timeout: Request timeout in seconds (default 60)
            user_agent: Custom User-Agent string (default BPR&D identification)
        """
        self.timeout = timeout
        self.session = requests.Session()

        # Identify ourselves properly to DOJ servers
        ua = user_agent or 'BPR&D Research Project (epstein-doj-analysis)'
        self.session.headers.update({
            'User-Agent': ua
        })

    def stream_pdf(self, url: str) -> io.BytesIO:
        """
        Stream PDF directly to memory buffer.

        Args:
            url: URL of PDF document on DOJ website

        Returns:
            BytesIO object containing PDF data (in RAM only)

        Raises:
            ValueError: If URL doesn't return valid PDF
            RuntimeError: If download fails

        Privacy Guarantee: No file creation - data streamed directly to RAM.
        """
        logger.info(f"Streaming PDF from: {url}")

        try:
            # Stream directly (NOT to file)
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            # Verify content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                # Some servers don't set Content-Type correctly, so we'll be lenient
                # but log a warning
                logger.warning(f"Unexpected content type: {content_type}")

            # Stream to memory buffer (NOT to file)
            pdf_buffer = io.BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    pdf_buffer.write(chunk)

            # Reset to start for reading
            pdf_buffer.seek(0)

            # Verify it's actually a PDF by checking magic bytes
            header = pdf_buffer.read(4)
            pdf_buffer.seek(0)  # Reset again

            if header != b'%PDF':
                raise ValueError(f"URL did not return valid PDF (header: {header})")

            size_mb = pdf_buffer.getbuffer().nbytes / (1024 * 1024)
            logger.info(f"Successfully streamed PDF ({size_mb:.2f} MB) to memory")

            return pdf_buffer

        except requests.exceptions.Timeout:
            raise RuntimeError(f"Timeout while downloading from {url}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to download PDF: {e}")

    def stream_url_to_bytes(self, url: str) -> bytes:
        """
        Alternative method that returns raw bytes instead of BytesIO.
        Useful for some processing scenarios.

        Args:
            url: URL of document to stream

        Returns:
            Raw bytes of document content

        Privacy Guarantee: No file creation - data streamed directly to RAM.
        """
        pdf_buffer = self.stream_pdf(url)
        return pdf_buffer.getvalue()

    def close(self):
        """Clean up session resources."""
        if self.session:
            self.session.close()
            logger.debug("Session closed")

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()

    def __del__(self):
        """Ensure session cleanup on garbage collection."""
        self.close()


# Privacy verification helper
def verify_no_file_operations():
    """
    Verification helper to ensure DocumentStreamer doesn't create files.

    This is a code-level assertion that should be enforced at runtime
    by PrivacyGuard, but we include it here as a double-check.
    """
    import inspect
    import builtins

    # Get DocumentStreamer source
    source = inspect.getsource(DocumentStreamer)

    # Forbidden operations that would create files
    forbidden = ['open(', 'write(', 'w"', "w'", 'wb"', "wb'", 'with open']

    for op in forbidden:
        if op in source:
            # Check if it's in a comment
            for line in source.split('\n'):
                if op in line and not line.strip().startswith('#'):
                    raise AssertionError(
                        f"DocumentStreamer contains forbidden file operation: {op}"
                    )

    return True


if __name__ == "__main__":
    # Simple test if run directly
    logging.basicConfig(level=logging.INFO)

    # Verify no file operations in source
    print("Verifying no file operations in DocumentStreamer source...")
    verify_no_file_operations()
    print("✓ Verification passed - no file operations detected")

    # Test with a sample DOJ document (if URL provided)
    # This would require an actual DOJ URL to test
    print("\nDocumentStreamer initialized successfully")
    print("Privacy guarantee: All PDF streaming happens in-memory only")
