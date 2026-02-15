import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scrape():
    url = "https://www.justice.gov/epstein"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        logger.info(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for PDF links
        pdf_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().endswith('.pdf'):
                # Handle relative URLs
                if href.startswith('/'):
                    href = "https://www.justice.gov" + href
                elif not href.startswith('http'):
                    href = "https://www.justice.gov/epstein/" + href # Rough guess

                pdf_links.append(href)

        logger.info(f"Found {len(pdf_links)} PDF links")
        for link in pdf_links[:5]:
            logger.info(f"  - {link}")

    except Exception as e:
        logger.error(f"Scraping failed: {e}")

if __name__ == "__main__":
    test_scrape()
