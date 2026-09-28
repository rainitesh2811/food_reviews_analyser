import sys
import os
import config
from src.analyzer.categorizer import analyze_reviews

if __name__ == "__main__":
    print("Starting Operational Service Lag Analyzer...\n")
    
    if not os.path.exists(config.RAW_CSV_PATH):
        print(f"[-] Scraped data file not found at: {config.RAW_CSV_PATH}")
        print("[-] Please run 'python main_scraper.py' first to collect review data.")
        sys.exit(1)

    analyze_reviews(config.RAW_CSV_PATH)