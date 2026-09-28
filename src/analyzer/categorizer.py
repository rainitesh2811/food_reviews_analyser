import os
import sys
import pandas as pd
from transformers import pipeline
import config

# Define operational categories
SERVICE_CATEGORIES = [
    "Delivery Delay / Speed",
    "Food Quality / Taste / Temp",
    "Missing / Wrong Items",
    "Packaging Issues",
    "Customer Support / Price"
]

print("[+] Loading Multi-Aspect Sentiment & Category Model...")
# Zero-shot model handles mixed sentiment classification
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def analyze_single_review(comment: str, rating: float):
    """
    Evaluates both the numerical rating and comment text for positive aspects
    and service lags.
    """
    if not isinstance(comment, str) or len(comment.strip()) < 5:
        # Fallback if comment is empty
        if rating >= 4:
            return {"sentiment": "Positive", "praises": ["Food Quality / Taste / Temp"], "lags": []}
        else:
            return {"sentiment": "Negative", "praises": [], "lags": ["Food Quality / Taste / Temp"]}

    # Classify comment aspect
    cat_result = classifier(comment, candidate_labels=SERVICE_CATEGORIES)
    primary_aspect = cat_result["labels"][0]

    # Zero-shot sentiment check on the comment itself
    sent_result = classifier(comment, candidate_labels=["positive feedback", "negative operational complaint"])
    comment_sentiment = sent_result["labels"][0]

    is_negative_comment = comment_sentiment == "negative operational complaint" or rating <= 3

    if is_negative_comment:
        return {
            "sentiment": "Negative / Mixed",
            "praises": [],
            "lags": [primary_aspect]
        }
    else:
        return {
            "sentiment": "Positive",
            "praises": [primary_aspect],
            "lags": []
        }

def analyze_reviews(raw_csv_path: str):
    if not os.path.exists(raw_csv_path):
        print(f"[-] Error: File not found at {raw_csv_path}")
        return

    df = pd.read_csv(raw_csv_path)
    if df.empty:
        print("[-] Error: Scraped CSV is empty.")
        return

    store_name = df["store_name"].iloc[0] if "store_name" in df.columns else "Target Restaurant"
    total_reviews = len(df)

    positive_count = 0
    negative_count = 0

    lag_counts = {}
    praise_counts = {}

    print(f"\n[+] Analyzing {total_reviews} total reviews (Ratings + Comment Sentiment)...")

    for _, row in df.iterrows():
        comment = row.get("review_comment", "")
        rating = float(row.get("review_rating", 3))

        result = analyze_single_review(comment, rating)

        if result["lags"]:
            negative_count += 1
            for lag in result["lags"]:
                lag_counts[lag] = lag_counts.get(lag, 0) + 1

        if result["praises"]:
            positive_count += 1
            for praise in result["praises"]:
                praise_counts[praise] = praise_counts.get(praise, 0) + 1

    # Sort results
    sorted_lags = sorted(lag_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_praises = sorted(praise_counts.items(), key=lambda x: x[1], reverse=True)

    # Build output string
    output_lines = []
    output_lines.append(f"=== Comprehensive Sentiment & Service Analysis: {store_name} ===")
    output_lines.append(f"Total Reviews Analyzed: {total_reviews}")
    output_lines.append(f"Positive Sentiment Reviews: {positive_count}")
    output_lines.append(f"Reviews with Service Lags (Low Rating / Mixed Comments): {negative_count}\n")

    output_lines.append("Top Performing Service Aspects:")
    if sorted_praises:
        for cat, count in sorted_praises:
            pct = round((count / total_reviews) * 100)
            output_lines.append(f"• {cat}: {pct}% ({count} reviews)")
    else:
        output_lines.append("• None highlighted")

    output_lines.append("\nService Lag Breakdown (Operational Bottlenecks):")
    top_lags = []
    if sorted_lags:
        for idx, (cat, count) in enumerate(sorted_lags):
            pct = round((count / total_reviews) * 100)
            flag = "  [CRITICAL LAG]" if idx == 0 else ""
            output_lines.append(f"- {cat}: {pct}% ({count} reviews){flag}")
            if idx < 2:
                top_lags.append(f'"{cat}"')
    else:
        output_lines.append("- No significant service lags detected!")

    # Recommendation summary
    if top_lags:
        if len(top_lags) > 1:
            rec_str = f"Final Recommendation: {store_name} is performing well overall, but primarily lagging in {top_lags[0]} and {top_lags[1]}."
        else:
            rec_str = f"Final Recommendation: {store_name} is performing well overall, but lagging in {top_lags[0]}."
    else:
        rec_str = f"Final Recommendation: {store_name} maintains high service standards across all aspects."

    output_lines.append(f"\n{rec_str}")

    final_output_text = "\n".join(output_lines)

    # Print to console
    print("\n" + final_output_text)

    # Save outputs
    report_txt_path = os.path.join(config.PROCESSED_DATA_DIR, "service_lag_summary.txt")
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write(final_output_text)

    report_data = []
    for cat, count in sorted_lags:
        report_data.append({
            "store_name": store_name,
            "metric_type": "Service Lag",
            "category": cat,
            "count": count,
            "percentage_of_total": round((count / total_reviews) * 100, 2)
        })

    pd.DataFrame(report_data).to_csv(config.REPORT_CSV_PATH, index=False)

if __name__ == "__main__":
    analyze_reviews(config.RAW_CSV_PATH)