import random
import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import config

def run_scraper_for_city(city_url: str, max_reviews: int = 50):
    reviews_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # Step 1: Navigate to City Directory
        print(f"[+] Step 1: Navigating to City Directory: {city_url}")
        page.goto(city_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Scroll to load listing cards
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(2000)

        # Step 2: Extract Restaurant Links
        restaurant_anchors = page.query_selector_all("a[href*='/info'], a[href*='/order'], a[href*='-locality']")
        
        valid_links = []
        for anchor in restaurant_anchors:
            href = anchor.get_attribute("href")
            if href and "/reviews" not in href and "/book" not in href:
                full_url = href if href.startswith("http") else "https://www.zomato.com" + href
                if full_url not in valid_links:
                    valid_links.append(full_url)

        if not valid_links:
            print("[-] No specific restaurant links found on the city page.")
            browser.close()
            return

        # Select a restaurant at random
        selected_restaurant_url = random.choice(valid_links)
        print(f"[+] Step 2: Randomly Selected Restaurant:\n    {selected_restaurant_url}")

        # Step 3: Open Selected Restaurant Page
        page.goto(selected_restaurant_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Extract store name
        try:
            store_name = page.inner_text("h1").strip().split("\n")[0]
        except Exception:
            store_name = "Selected Restaurant"

        print(f"[+] Step 3: Restaurant Name: {store_name}")

        # Step 4: Click the 'Reviews' Tab
        try:
            print("[+] Step 4: Navigating to 'Reviews' tab...")
            reviews_tab = page.query_selector("a:has-text('Reviews'), div:has-text('Reviews')")
            if reviews_tab:
                reviews_tab.click()
                page.wait_for_timeout(3000)
            else:
                reviews_url = selected_restaurant_url.rstrip("/") + "/reviews"
                page.goto(reviews_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
        except Exception as e:
            print(f"[-] Tab navigation note: {e}")

        # Scroll down to load reviews feed
        print("[+] Step 5: Scrolling review feed...")
        for _ in range(8):
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(1500)

        # Step 5: Extract Reviews and Dynamic Star Ratings
        # Locate paragraph elements containing review text
        review_cards = page.query_selector_all("p, span")
        
        extracted_reviews = []
        for card in review_cards:
            try:
                text = card.inner_text().strip()
                # Filter out short text and navigation header noise
                if len(text) > 30 and not any(text.startswith(x) for x in ["Overview", "Dining", "Book", "Closes", "Open"]):
                    if not any(r["review_comment"] == text for r in extracted_reviews):
                        
                        # Dynamic Rating Extraction: Search parent elements for rating numbers (e.g. "5.0", "1", "4★")
                        parent = card.query_selector("xpath=..")
                        rating_val = 5  # Default baseline rating if unparsed
                        
                        if parent:
                            parent_text = parent.inner_text()
                            match = re.search(r'\b([1-5](\.\d)?)\b', parent_text)
                            if match:
                                rating_val = float(match.group(1))

                        extracted_reviews.append({
                            "store_name": store_name,
                            "review_rating": rating_val,
                            "review_comment": text,
                            "timestamp": time.strftime("%Y-%m-%d")
                        })
            except Exception:
                continue

        print(f"[+] Captured {len(extracted_reviews)} user reviews with ratings.")
        reviews_data = extracted_reviews[:max_reviews]

        browser.close()

    if reviews_data:
        df = pd.DataFrame(reviews_data)
        df.to_csv(config.RAW_CSV_PATH, index=False)
        print(f"\n[✓] Saved raw ratings and comments to: {config.RAW_CSV_PATH}")
    else:
        print("[-] No review comments captured.")

if __name__ == "__main__":
    city_directory_url = input("Enter City Directory URL (e.g., https://www.zomato.com/alwar/restaurants): ").strip()
    run_scraper_for_city(city_directory_url)
    # Add this at the bottom of src/scraper/collector.py

def run_scraper(target_url: str, max_reviews: int = 50):
    """Wrapper function to align with main_scraper.py"""
    return run_scraper_for_city(city_url=target_url, max_reviews=max_reviews)