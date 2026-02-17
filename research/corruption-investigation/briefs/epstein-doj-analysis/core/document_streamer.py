"""
Document streamer that NEVER writes to disk.
All operations in-memory only.

CRITICAL: This module is the foundation of our privacy guarantee.
NO file I/O operations allowed - all data stays in RAM.

Updated to use curl_cffi for browser impersonation (Tier 2 Anti-Bot Bypass).
"""
import io
import time
import random
from typing import Optional
import logging
# Use curl_cffi.requests instead of standard requests to spoof TLS/JA3 fingerprint
from curl_cffi import requests

logger = logging.getLogger(__name__)


class DocumentStreamer:
    """
    Stream PDFs from DOJ/Court websites directly to memory.
    Uses browser impersonation to bypass Akamai/Cloudflare blocks.

    Privacy Guarantee: Zero file I/O operations, all data stays in RAM.
    """

    def __init__(self, timeout: int = 60, user_agent: str = None):
        """
        Initialize document streamer with browser impersonation.

        Args:
            timeout: Request timeout in seconds (default 60)
            user_agent: Custom User-Agent (overridden by impersonate="chrome124")
        """
        self.timeout = timeout
        # Using Session from curl_cffi to maintain cookies/headers
        self.session = requests.Session()

        # Default "Polite" Headers for Tier 2 Strategy
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        })

    def stream_pdf(self, url: str) -> io.BytesIO:
        """
        Stream PDF directly to memory buffer.

        Args:
            url: URL of PDF document

        Returns:
            BytesIO object containing PDF data (in RAM only)

        Raises:
            ValueError: If URL doesn't return valid PDF
            RuntimeError: If download fails

        Privacy Guarantee: No file creation - data streamed directly to RAM.
        """
        logger.info(f"Streaming PDF from: {url}")

        # Tier 2: Random delay + Exponential backoff (simulated here with simple sleep)
        # sleep_time = random.uniform(2, 5) # Reduced for trial speed, increase for production
        # time.sleep(sleep_time)

        try:
            # Stream directly (NOT to file)
            # impersonate="chrome124" is the magic key for Tier 2 bypass
            response = self.session.get(
                url,
                stream=True,
                timeout=self.timeout,
                impersonate="chrome124"
            )
            response.raise_for_status()

            # Verify content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")

            # Stream to memory buffer (NOT to file)
            pdf_buffer = io.BytesIO()

            # Note: curl_cffi stream iterator usage
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    pdf_buffer.write(chunk)

            # Reset to start for reading
            pdf_buffer.seek(0)

            # Verify it's actually a PDF by checking magic bytes
            header = pdf_buffer.read(4)
            pdf_buffer.seek(0)  # Reset again

            if header != b'%PDF':
                # Sometimes we get HTML error pages disguised as 200 OK
                # Try to read first 100 bytes to see what we got
                preview = header + pdf_buffer.read(100)
                pdf_buffer.seek(0)
                logger.error(f"Invalid PDF header: {preview}")
                raise ValueError(f"URL did not return valid PDF (header: {header})")

            size_mb = pdf_buffer.getbuffer().nbytes / (1024 * 1024)
            logger.info(f"Successfully streamed PDF ({size_mb:.2f} MB) to memory")

            return pdf_buffer

        except requests.RequestsError as e:
            raise RuntimeError(f"Failed to download PDF (curl_cffi): {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to download PDF: {e}")

    def stream_url_to_bytes(self, url: str) -> bytes:
        """
        Alternative method that returns raw bytes instead of BytesIO.
        """
        pdf_buffer = self.stream_pdf(url)
        return pdf_buffer.getvalue()

    def close(self):
        """Clean up session resources."""
        if self.session:
            self.session.close()
            logger.debug("Session closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


# Privacy verification helper
def verify_no_file_operations():
    """
    Verification helper to ensure DocumentStreamer doesn't create files.
    """
    import inspect

    source = inspect.getsource(DocumentStreamer)
    forbidden = ['open(', 'write(', 'w"', "w'", 'wb"', "wb'", 'with open']

    for op in forbidden:
        if op in source:
            for line in source.split('\n'):
                if op in line and not line.strip().startswith('#'):
                    # Allow pdf_buffer.write() as it is BytesIO
                    if "pdf_buffer.write" in line:
                        continue
                    raise AssertionError(
                        f"DocumentStreamer contains forbidden file operation: {op}"
                    )

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Verifying no file operations...")
    verify_no_file_operations()
    print("✓ Verification passed")
