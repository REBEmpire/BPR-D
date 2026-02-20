import time
import os
import argparse
from playwright.sync_api import sync_playwright

def verify_research_pages(base_url):
    """
    Automates a browser to visit the research listing and a specific brief,
    capturing screenshots for verification.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Visit Research Listing Page
        base_url = base_url.rstrip('/')
        research_url = f"{base_url}/research"
        print(f"Navigating to Research Listing Page: {research_url}...")
        try:
            page.goto(research_url)
            # Wait for content to load
            page.wait_for_selector("text=Daily Research Briefs")
            # Take screenshot of listing
            page.screenshot(path="verification/research_listing.png")
            print("Captured listing page screenshot.")
        except Exception as e:
            print(f"Error on listing page: {e}")

        # 2. Visit a Specific Brief (Direct Navigation)
        # Using the expected slug for the Neuralink brief
        detail_url = f"{base_url}/research/high-tech/2026-02-13-neuralink"
        print(f"Navigating to Neuralink Brief: {detail_url}...")
        try:
            page.goto(detail_url)
            # Wait for content to load
            page.wait_for_selector("h1")
            # Take screenshot of detail page
            page.screenshot(path="verification/research_detail.png")
            print("Captured detail page screenshot.")
        except Exception as e:
            print(f"Error on detail page: {e}")

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Research Pages")
    parser.add_argument(
        "--url",
        help="Base URL for the application (default: RESEARCH_BASE_URL env var or http://localhost:3000)",
        default=os.getenv("RESEARCH_BASE_URL", "http://localhost:3000")
    )
    args = parser.parse_args()

    # Give the server a moment to start up if it was just launched
    time.sleep(5)
    verify_research_pages(args.url)
