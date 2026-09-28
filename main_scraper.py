import sys
from src.scraper.collector import run_scraper_for_city

if __name__ == "__main__":
    url = input("Enter Food Delivery Target Directory URL: ").strip()
    if not url:
        print("URL required to proceed.")
        sys.exit(1)

    print("\nStarting Scraper Network...")
    run_scraper_for_city(city_url=url, max_reviews=50)