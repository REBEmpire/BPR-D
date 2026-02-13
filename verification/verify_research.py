import time
from playwright.sync_api import sync_playwright

def verify_research_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Visit Research Listing Page
        print("Navigating to Research Listing Page...")
        try:
            page.goto("http://localhost:3000/research")
            # Wait for content to load
            page.wait_for_selector("text=Daily Research Briefs")
            # Take screenshot of listing
            page.screenshot(path="verification/research_listing.png")
            print("Captured listing page screenshot.")
        except Exception as e:
            print(f"Error on listing page: {e}")

        # 2. Visit a Specific Brief
        print("Navigating to Neuralink Brief...")
        try:
            # Click on the Neuralink card
            page.click("text=Neuralink & The Ultimate DRM")
            # Wait for content to load
            page.wait_for_selector("h1")
            # Take screenshot of detail page
            page.screenshot(path="verification/research_detail.png")
            print("Captured detail page screenshot.")
        except Exception as e:
            print(f"Error on detail page: {e}")

        browser.close()

if __name__ == "__main__":
    # Give the server a moment to start up if it was just launched
    time.sleep(5)
    verify_research_pages()
