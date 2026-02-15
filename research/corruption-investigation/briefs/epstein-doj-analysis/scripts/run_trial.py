"""
Trial Run Script for DOJ Epstein Document Analysis.

Fetches 10 real documents (from DOJ or fallback mirrors) and processes them
to verify the end-to-end pipeline and Hugging Face integration.
"""
import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.document_streamer import DocumentStreamer
from core.document_processor import DocumentProcessor
from core.hf_dataset_client import HFDatasetClient
from config.url_mappings import DOJDatasetConfig
from utils.privacy_guard import PrivacyGuard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_trial():
    print("=" * 70)
    print("DOJ EPSTEIN DOCUMENT ANALYSIS - TRIAL RUN (10 Real Docs)")
    print("=" * 70)

    # Initialize components
    print("Initializing components...")

    # Use a standard browser UA to avoid blocking
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    doc_streamer = DocumentStreamer(user_agent=ua)
    doc_processor = DocumentProcessor()
    hf_client = HFDatasetClient()
    privacy_guard = PrivacyGuard(watch_dir=str(project_root))

    print("✓ Components initialized")

    # Privacy check
    privacy_guard.verify_no_local_storage_active()
    print("✓ Privacy check passed")

    # Fetch URLs
    print("\nFetching document URLs...")
    # Fetch 10 URLs
    urls = DOJDatasetConfig.get_dataset_urls(1, count=10)

    if not urls:
        print("✗ No URLs found! Aborting trial.")
        return

    print(f"Found {len(urls)} URLs to process.")

    success_count = 0

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")

        try:
            # Stream PDF
            start_time = time.time()
            pdf_stream = doc_streamer.stream_pdf(url)
            stream_time = time.time() - start_time
            print(f"  ✓ Streamed in {stream_time:.2f}s")

            # Process
            start_time = time.time()
            analysis = doc_processor.process_document(
                pdf_stream=pdf_stream,
                source_url=url,
                dataset_num=1
            )
            process_time = time.time() - start_time
            print(f"  ✓ Processed in {process_time:.2f}s")

            # Save to HF
            start_time = time.time()
            hf_client.add_document_analysis(analysis)
            save_time = time.time() - start_time
            print(f"  ✓ Saved to HF in {save_time:.2f}s")

            success_count += 1

        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 70)
    print(f"TRIAL COMPLETE: {success_count}/{len(urls)} successful")
    print("=" * 70)

if __name__ == "__main__":
    run_trial()
