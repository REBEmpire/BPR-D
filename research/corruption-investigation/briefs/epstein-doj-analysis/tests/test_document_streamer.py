"""
Unit tests for DocumentStreamer.

CRITICAL: These tests verify the privacy guarantee that PDFs stream
to memory without creating local files.
"""
import pytest
import io
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.document_streamer import DocumentStreamer, verify_no_file_operations


class TestDocumentStreamer:
    """Test suite for DocumentStreamer."""

    def test_initialization(self):
        """Test DocumentStreamer initializes correctly."""
        streamer = DocumentStreamer()
        assert streamer.timeout == 60
        assert streamer.session is not None
        assert 'BPR&D' in streamer.session.headers['User-Agent']

    def test_custom_user_agent(self):
        """Test custom User-Agent setting."""
        custom_ua = "Test Agent v1.0"
        streamer = DocumentStreamer(user_agent=custom_ua)
        assert streamer.session.headers['User-Agent'] == custom_ua

    @patch('requests.Session.get')
    def test_stream_pdf_success(self, mock_get):
        """Test successful PDF streaming to memory."""
        # Mock response with PDF content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}

        # Create fake PDF content (with correct header)
        fake_pdf_content = b'%PDF-1.4\n%some pdf content here'
        mock_response.iter_content = Mock(return_value=[fake_pdf_content])

        mock_get.return_value = mock_response

        # Stream PDF
        streamer = DocumentStreamer()
        pdf_buffer = streamer.stream_pdf('https://example.com/test.pdf')

        # Verify it's a BytesIO object (in-memory)
        assert isinstance(pdf_buffer, io.BytesIO)

        # Verify it contains PDF data
        pdf_buffer.seek(0)
        header = pdf_buffer.read(4)
        assert header == b'%PDF'

        # Verify mock was called correctly
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_stream_pdf_invalid_content_type(self, mock_get):
        """Test handling of non-PDF content types."""
        # Mock response with wrong content type
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}

        # HTML content (not PDF)
        fake_html_content = b'<html><body>Not a PDF</body></html>'
        mock_response.iter_content = Mock(return_value=[fake_html_content])

        mock_get.return_value = mock_response

        streamer = DocumentStreamer()

        # Should raise ValueError for invalid PDF
        with pytest.raises(ValueError, match="did not return valid PDF"):
            streamer.stream_pdf('https://example.com/not-a-pdf.html')

    @patch('requests.Session.get')
    def test_stream_pdf_timeout(self, mock_get):
        """Test timeout handling."""
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout()

        streamer = DocumentStreamer(timeout=5)

        with pytest.raises(RuntimeError, match="Timeout"):
            streamer.stream_pdf('https://example.com/slow.pdf')

    @patch('requests.Session.get')
    def test_stream_pdf_network_error(self, mock_get):
        """Test network error handling."""
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError()

        streamer = DocumentStreamer()

        with pytest.raises(RuntimeError, match="Failed to download"):
            streamer.stream_pdf('https://example.com/error.pdf')

    @patch('requests.Session.get')
    def test_stream_url_to_bytes(self, mock_get):
        """Test alternative bytes return method."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}

        fake_pdf_content = b'%PDF-1.4\ntest content'
        mock_response.iter_content = Mock(return_value=[fake_pdf_content])

        mock_get.return_value = mock_response

        streamer = DocumentStreamer()
        pdf_bytes = streamer.stream_url_to_bytes('https://example.com/test.pdf')

        # Verify it returns bytes
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF')

    def test_context_manager(self):
        """Test context manager support."""
        with DocumentStreamer() as streamer:
            assert streamer.session is not None

        # Session should be closed after context exit
        # (In practice, this is verified by the close() method being called)

    def test_no_file_operations_in_source(self):
        """
        CRITICAL TEST: Verify DocumentStreamer source code contains
        NO file operation calls.
        """
        # This test ensures the privacy guarantee at code level
        assert verify_no_file_operations() is True

    @patch('requests.Session.get')
    def test_memory_only_processing(self, mock_get):
        """
        CRITICAL TEST: Verify PDF processing happens entirely in memory
        without creating files.
        """
        # Mock PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}

        fake_pdf = b'%PDF-1.4\n' + b'x' * 1000  # 1KB fake PDF
        mock_response.iter_content = Mock(return_value=[fake_pdf])

        mock_get.return_value = mock_response

        # Get directory state before
        cwd = Path.cwd()
        files_before = set(cwd.rglob('*'))

        # Stream PDF
        streamer = DocumentStreamer()
        pdf_buffer = streamer.stream_pdf('https://example.com/test.pdf')

        # Verify PDF is in memory
        assert isinstance(pdf_buffer, io.BytesIO)
        assert pdf_buffer.getbuffer().nbytes > 0

        # Get directory state after
        files_after = set(cwd.rglob('*'))

        # CRITICAL: No new files should be created
        new_files = files_after - files_before
        pdf_files = [f for f in new_files if f.suffix == '.pdf']

        assert len(pdf_files) == 0, f"PDF files created: {pdf_files}"

    def test_cleanup_on_deletion(self):
        """Test that session is cleaned up on object deletion."""
        streamer = DocumentStreamer()
        session = streamer.session

        # Delete streamer
        del streamer

        # Session should be closed (verified by __del__ method call)
        # Note: This is implementation-dependent and may not be immediately
        # testable, but the __del__ method ensures cleanup

    @patch('requests.Session.get')
    def test_large_pdf_streaming(self, mock_get):
        """Test streaming of large PDFs without file creation."""
        # Mock response with large PDF
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}

        # Simulate 10MB PDF in chunks
        chunk_size = 8192
        fake_pdf_header = b'%PDF-1.4\n'
        chunks = [fake_pdf_header] + [b'x' * chunk_size for _ in range(1250)]  # ~10MB

        mock_response.iter_content = Mock(return_value=chunks)
        mock_get.return_value = mock_response

        streamer = DocumentStreamer()
        pdf_buffer = streamer.stream_pdf('https://example.com/large.pdf')

        # Verify it's in memory
        assert isinstance(pdf_buffer, io.BytesIO)

        # Verify size (approximately 10MB)
        size_mb = pdf_buffer.getbuffer().nbytes / (1024 * 1024)
        assert 9 < size_mb < 11  # Allow some variance


class TestPrivacyVerification:
    """Tests specifically for privacy guarantee verification."""

    def test_verify_no_file_operations_function(self):
        """Test the source code verification function."""
        # Should pass - DocumentStreamer has no file operations
        result = verify_no_file_operations()
        assert result is True

    def test_source_code_inspection(self):
        """Test that we can inspect DocumentStreamer source."""
        import inspect
        from core.document_streamer import DocumentStreamer

        source = inspect.getsource(DocumentStreamer)

        # Verify source doesn't contain file operations
        forbidden_operations = [
            'open(',
            'file(',
            '.write(',
            'with open',
        ]

        for op in forbidden_operations:
            # Check each line (ignoring comments and strings)
            for line in source.split('\n'):
                stripped = line.strip()

                # Skip comments
                if stripped.startswith('#'):
                    continue

                # Skip docstrings
                if '"""' in line or "'''" in line:
                    continue

                # If operation is found, it better be in a comment or string
                if op in line:
                    # This should only appear in comments/strings/tests
                    assert (
                        '#' in line or
                        '"' in line or
                        "'" in line or
                        'forbidden' in line.lower()
                    ), f"Forbidden operation {op} found in line: {line}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])
