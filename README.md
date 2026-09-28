# Food Delivery App Scraper & Service Lag Analyzer

A modular Python application built with **Playwright** and **HuggingFace Transformers (BART Zero-Shot Classification)** to scrape food delivery platforms (e.g., Zomato), extract customer reviews/ratings, and detect primary operational service bottlenecks (Delivery Delays, Food Quality, Missing Items, etc.).

## Project Structure
- `src/scraper/`: Playwright web scraper for dynamic pages and review tab navigation.
- `src/analyzer/`: Zero-Shot NLP Engine for aspect-based sentiment and service lag evaluation.
- `data/`: Contains raw scraped CSVs and processed service lag reports.

## Setup & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
