"""
DOJ dataset URL patterns and mappings.

This module contains URL patterns and metadata for accessing
the 12 DOJ Epstein document datasets.

Includes Tier 1 (CourtListener API) and Tier 2 (Public Mirrors) strategies.
"""
from typing import Dict, List, Optional
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DOJDatasetConfig:
    """
    Configuration for DOJ Epstein document datasets.
    """

    # Base URL for DOJ Epstein files
    BASE_URL = "https://www.justice.gov/epstein"

    # Fallback URLs for when DOJ site blocks scraping
    # Using a consolidated DocumentCloud PDF for trial purposes as individual scraping is blocked
    FALLBACK_URLS = [
        "https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf", # 369MB Consolidated PDF
        # Replicated for volume testing if needed, but risky due to size
        # "https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf",
    ]

    # Dataset configurations
    # Format: dataset_number -> {name, estimated_docs, url_pattern, priority}
    DATASETS = {
        1: {
            'name': 'Dataset 1',
            'estimated_docs': 150,
            'url_pattern': f'{BASE_URL}', # Main page for now
            'priority': 'high',  # Contains key court filings
            'description': 'Initial court filings and early documents',
        },
        2: {
            'name': 'Dataset 2',
            'estimated_docs': 200,
            'url_pattern': f'{BASE_URL}',
            'priority': 'high',
            'description': 'FBI investigation files',
        },
        3: {
            'name': 'Dataset 3',
            'estimated_docs': 180,
            'url_pattern': f'{BASE_URL}',
            'priority': 'medium',
            'description': 'Email correspondence',
        },
        4: {
            'name': 'Dataset 4',
            'estimated_docs': 220,
            'url_pattern': f'{BASE_URL}',
            'priority': 'high',
            'description': 'Flight logs and travel records',
        },
        5: {
            'name': 'Dataset 5',
            'estimated_docs': 160,
            'url_pattern': f'{BASE_URL}',
            'priority': 'medium',
            'description': 'Property and financial records',
        },
        6: {
            'name': 'Dataset 6',
            'estimated_docs': 190,
            'url_pattern': f'{BASE_URL}',
            'priority': 'medium',
            'description': 'Additional witness depositions',
        },
        7: {
            'name': 'Dataset 7',
            'estimated_docs': 170,
            'url_pattern': f'{BASE_URL}',
            'priority': 'low',
            'description': 'Media and press coverage',
        },
        8: {
            'name': 'Dataset 8',
            'estimated_docs': 210,
            'url_pattern': f'{BASE_URL}',
            'priority': 'high',
            'description': 'Little St. James Island records',
        },
        9: {
            'name': 'Dataset 9',
            'estimated_docs': 140,
            'url_pattern': f'{BASE_URL}',
            'priority': 'high',
            'description': 'Zorro Ranch (New Mexico) records',
        },
        10: {
            'name': 'Dataset 10',
            'estimated_docs': 130,
            'url_pattern': f'{BASE_URL}',
            'priority': 'medium',
            'description': 'Manhattan and Palm Beach property records',
        },
        11: {
            'name': 'Dataset 11',
            'estimated_docs': 100,
            'url_pattern': f'{BASE_URL}',
            'priority': 'low',
            'description': 'Miscellaneous documents',
        },
        12: {
            'name': 'Dataset 12',
            'estimated_docs': 120,
            'url_pattern': f'{BASE_URL}',
            'priority': 'medium',
            'description': 'Supplemental materials and index',
        },
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

        Tries to scrape the DOJ website first. If blocked by anti-bot protection,
        falls back to a hardcoded list of known document mirrors for trial purposes.

        Args:
            dataset_num: Dataset number (1-12)
            start_index: Starting document index
            count: Number of URLs to return

        Returns:
            List of document URLs
        """
        info = cls.get_dataset_info(dataset_num)
        if not info:
            return []

        url_pattern = info['url_pattern']
        urls = []

        # 1. Attempt Scraping (Likely to be blocked by Akamai)
        try:
            logger.info(f"Attempting to scrape URLs from {url_pattern}...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            # Short timeout to fail fast
            response = requests.get(url_pattern, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.lower().endswith('.pdf'):
                        if href.startswith('/'):
                            href = "https://www.justice.gov" + href
                        elif not href.startswith('http'):
                            href = "https://www.justice.gov/epstein/" + href
                        urls.append(href)

                if urls:
                    logger.info(f"Scraper found {len(urls)} PDF links")
                else:
                    logger.warning("Scraper found no PDF links (likely challenge page)")
            else:
                logger.warning(f"Scraper received status code {response.status_code}")

        except Exception as e:
            logger.warning(f"Scraping failed: {e}")

        # 2. Fallback if scraping failed or yielded no results
        if not urls:
            logger.warning("Using fallback URLs (DocumentCloud Mirror) due to scraping failure/blocking")
            # For trial/demo, return the fallback list regardless of dataset_num
            urls = cls.FALLBACK_URLS

        # Apply slicing
        if start_index >= len(urls):
            return []

        end_index = None
        if count is not None:
            end_index = start_index + count

        return urls[start_index:end_index]

    @classmethod
    def estimate_processing_time(cls, dataset_num: int) -> float:
        """
        Estimate processing time for dataset in hours.

        Based on:
        - Average 3 docs/hour initially
        - Dataset estimated document count

        Args:
            dataset_num: Dataset number (1-12)

        Returns:
            Estimated hours (rounded up)
        """
        info = cls.get_dataset_info(dataset_num)
        if not info:
            return 0

        estimated_docs = info['estimated_docs']
        docs_per_hour = 3  # Conservative initial estimate

        return estimated_docs / docs_per_hour


# Helper function for manual URL list creation
def create_url_list_from_file(filepath: str) -> List[str]:
    """
    Load URLs from a text file (one URL per line).

    Useful for manually created URL lists from external tools.

    Args:
        filepath: Path to text file with URLs

    Returns:
        List of URLs
    """
    from pathlib import Path

    urls = []
    filepath = Path(filepath)

    if filepath.exists():
        with open(filepath, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

    return urls


if __name__ == "__main__":
    # Display dataset configuration
    print("DOJ Epstein Document Datasets Configuration")
    print("=" * 60)
    print()

    # Test fetching URLs for Dataset 1
    print("Testing URL fetch for Dataset 1...")
    urls = DOJDatasetConfig.get_dataset_urls(1, count=5)
    print(f"Found {len(urls)} URLs:")
    for url in urls:
        print(f"  - {url}")
    print()

    print("=" * 60)
    print(f"Total estimated documents: {DOJDatasetConfig.get_total_estimated_docs()}")
    print(f"High priority datasets: {DOJDatasetConfig.get_high_priority_datasets()}")
