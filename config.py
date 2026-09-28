import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Ensure output directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# File Paths
RAW_CSV_PATH = os.path.join(RAW_DATA_DIR, "raw_restaurant_reviews.csv")
REPORT_CSV_PATH = os.path.join(PROCESSED_DATA_DIR, "service_lag_report.csv")