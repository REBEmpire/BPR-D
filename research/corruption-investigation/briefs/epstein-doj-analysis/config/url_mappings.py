"""
DOJ dataset URL patterns and mappings.

This module contains URL patterns and metadata for accessing
the 12 DOJ Epstein document datasets.

Includes Tier 1 (CourtListener API) and Tier 2 (Public Mirrors) strategies.
"""
from typing import Dict, List, Optional
import logging
from core.court_listener import CourtListenerClient

logger = logging.getLogger(__name__)


class DOJDatasetConfig:
    """
    Configuration for DOJ Epstein document datasets.
    """

    # Base URL for DOJ Epstein files
    BASE_URL = "https://www.justice.gov/epstein"

    # Fallback URLs (Tier 2 - Mirrors)
    # Used if API fails or for specific known docs not in recent RECAP
    FALLBACK_URLS = [
        "https://www.courthousenews.com/wp-content/uploads/2019/07/Epstein-Indictment.pdf",
        "https://www.documentcloud.org/documents/1508273-jeffrey-epstein-flight-logs.pdf",
        "https://upload.wikimedia.org/wikipedia/commons/e/e4/Epstein_Palm_Beach_Search_Warrant.pdf",
        "https://int.nyt.com/data/documenthelper/1336-epstein-bail-request/2827602052b0472e35e7/optimized/full.pdf",
        "https://epsteinvcp.com/wp-content/uploads/2020/06/Epstein-Victims-Compensation-Program-Protocol.pdf"
    ]

    # Dataset configurations (Metadata placeholder)
    DATASETS = {
        1: {'name': 'Dataset 1', 'priority': 'high', 'description': 'Court Filings'},
        2: {'name': 'Dataset 2', 'priority': 'high', 'description': 'FBI Files'},
        # ... (simplified for brevity in this dynamic fetch version)
    }

    @classmethod
    def get_dataset_urls(
        cls,
        dataset_num: int,
        start_index: int = 0,
        count: int = None
    ) -> List[str]:
        """
        Get document URLs.

        Strategy:
        1. Try Tier 1: CourtListener RECAP API (Dynamic, Authentic)
        2. Fallback to Tier 2: Static Mirror List

        Args:
            dataset_num: Dataset number (1-12)
            start_index: Starting document index
            count: Number of URLs to return

        Returns:
            List of document URLs
        """
        target_count = count or 10
        urls = []

        # Tier 1: CourtListener API
        try:
            logger.info("Attempting Tier 1 fetch (CourtListener API)...")
            client = CourtListenerClient()
            # Fetch fresh URLs from SDNY / Maxwell dockets
            api_urls = client.get_epstein_docs(limit=target_count + start_index)

            if api_urls:
                # Apply slicing
                urls = api_urls[start_index : start_index + target_count]
                logger.info(f"Tier 1 success: Found {len(urls)} URLs")
            else:
                logger.warning("Tier 1 returned no URLs")

        except Exception as e:
            logger.error(f"Tier 1 fetch failed: {e}")

        # Tier 2: Fallback Mirrors
        if not urls:
            logger.warning("Falling back to Tier 2 (Static Mirrors)")
            urls = cls.FALLBACK_URLS

            # Apply slicing
            if start_index < len(urls):
                end = start_index + target_count
                urls = urls[start_index:end]
            else:
                urls = []

        return urls

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing Dynamic URL Fetch...")
    urls = DOJDatasetConfig.get_dataset_urls(1, count=5)
    print(f"Result: {len(urls)} URLs")
    for u in urls:
        print(f" - {u}")
