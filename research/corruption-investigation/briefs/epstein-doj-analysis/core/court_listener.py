"""
CourtListener RECAP API Client (Tier 1 Source).

Provides authenticated, API-based access to the RECAP archive of federal court documents.
This is the "Golden Ticket" for bypassing anti-bot measures on scraping.
"""
import logging
import requests
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

class CourtListenerClient:
    """Client for CourtListener v4 REST API."""

    BASE_URL = "https://www.courtlistener.com/api/rest/v4"

    def __init__(self, token: str = None):
        """
        Initialize client.

        Args:
            token: Optional API token (increases rate limits)
        """
        self.token = token or os.getenv('COURTLISTENER_TOKEN')
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({'Authorization': f'Token {self.token}'})

        # Identify ourselves
        self.session.headers.update({
            'User-Agent': 'BPR&D Research Project (epstein-analysis)'
        })

    def search_dockets(self, query: str = "Epstein", court: str = None) -> List[Dict]:
        """
        Search for dockets containing a query string.

        Args:
            query: Search term (e.g., "Epstein", "Maxwell")
            court: Optional court ID (e.g., "nysd" for SDNY)

        Returns:
            List of docket dictionaries
        """
        endpoint = f"{self.BASE_URL}/dockets/"
        params = {"party_name": query}
        if court:
            params["court"] = court

        try:
            logger.info(f"Searching dockets for '{query}'...")
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])
            logger.info(f"Found {len(results)} dockets")
            return results
        except Exception as e:
            logger.error(f"Docket search failed: {e}")
            return []

    def get_recap_documents(self, docket_id: int) -> List[Dict]:
        """
        Get RECAP documents for a specific docket.

        Args:
            docket_id: The CourtListener ID of the docket

        Returns:
            List of document dictionaries with 'filepath_local'
        """
        # Note: The 'recap_documents' field in docket object is a URL
        # But we can also query the 'recap-documents' endpoint filtering by docket
        endpoint = f"{self.BASE_URL}/recap-documents/"
        params = {"docket": docket_id}

        try:
            logger.info(f"Fetching documents for docket {docket_id}...")
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])

            # Filter for PDFs only
            pdfs = [
                doc for doc in results
                if doc.get('filepath_local') and doc.get('is_available')
            ]

            logger.info(f"Found {len(pdfs)} available PDFs")
            return pdfs
        except Exception as e:
            logger.error(f"Document fetch failed: {e}")
            return []

    def get_epstein_docs(self, limit: int = 10) -> List[str]:
        """
        High-level helper to get valid PDF URLs for Epstein-related cases.

        Args:
            limit: Max number of URLs to return

        Returns:
            List of direct PDF URLs (from CourtListener storage)
        """
        urls = []

        # Priority Dockets (Giuffre v Maxwell, US v Epstein)
        # We can search dynamically or use known good docket IDs if search is fuzzy
        # Search for "Maxwell" in SDNY (Giuffre v Maxwell is huge)
        dockets = self.search_dockets(query="Maxwell", court="nysd")

        for docket in dockets:
            if len(urls) >= limit:
                break

            docs = self.get_recap_documents(docket['id'])
            for doc in docs:
                # CourtListener hosts files at storage.courtlistener.com
                # We need to construct the full URL if filepath_local is relative
                # Usually filepath_local is like /absolute/path/to/file on their S3
                # But the API often returns the full URL in 'file_url' or similar?
                # Let's check the API response format in usage.
                # Actually, 'filepath_local' usually needs a base.
                # Ideally use 'absolute_url' if available or construct it.
                # For RECAP, the accessible URL is usually:
                # https://storage.courtlistener.com/recap/{filepath_local} (stripped of leading /)

                path = doc.get('filepath_local')
                if path:
                    # Remove leading 'storage/' if present, or just ensure correct base
                    # RECAP paths are usually: /gov.uscourts.nysd.443657/....
                    # Correct base: https://storage.courtlistener.com/recap

                    if path.startswith('/'):
                        path = path[1:]

                    url = f"https://storage.courtlistener.com/recap/{path}"
                    urls.append(url)

                    if len(urls) >= limit:
                        break

        return urls

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = CourtListenerClient()
    urls = client.get_epstein_docs(limit=5)
    print(f"Found {len(urls)} URLs:")
    for u in urls:
        print(f" - {u}")
