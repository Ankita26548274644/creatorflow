"""
Quick manual test for the feature engineering module.
Run from backend/: python test_features.py
"""
import pandas as pd
from app.services.cleaning import clean_dataframe
from app.services.features import engineer_features, VADER_AVAILABLE


def make_clean_df():
    """A small but realistic cleaned DataFrame."""
    return pd.DataFrame({
        "post_id": list(range(1, 11)),
        "date": pd.to_datetime([
            "2024-01-01 09:00", "2024-01-02 14:30", "2024-01-03 20:15",
            "2024-01-05 08:00", "2024-01-06 22:45", "2024-01-08 12:00",
            "2024-01-10 18:30", "2024-01-12 07:15", "2024-01-15 21:00",
            "2024-01-18 13:45",
        ]),
        "caption": [
            "Good morning everyone! #morning #vibes",
            "Check this out @friend 😊",
            "Late night thoughts",
            "Weekend plans #weekend",
            "Vibes only ✨✨✨",
            "New post! https://example.com #link",
            "Feeling happy today 😀",
            "Back to work #monday",
            "Reflecting on the week",
            "Just posted something new",
        ],
        "likes": [45, 78, 120, 90, 210, 60, 95, 130, 175, 88],
        "comments": [5, 12, 18, 10, 30, 8, 14, 20, 25, 11],
        "shares": [2, 6, 10, 4, 15, 3, 7, 9, 12, 5],
        "impressions": [500, 800, 1200, 900, 2000, 700, 1000, 1300, 1800, 950],
        "caption_missing": [0] * 10,
    })


if __name__ == "__main__":
    print("VADER available:", VADER_AVAILABLE)

    df = make_clean_df()
    print("\n" + "=" * 60)
    print("CLEANED INPUT")
    print("=" * 60)
    print(df[["post_id", "date", "caption", "likes", "comments",
              "shares", "impressions"]].to_string(index=False))

    featured, report = engineer_features(df)

    print("\n" + "=" * 60)
    print("FEATURE-ENGINEERED OUTPUT (all columns)")
    print("=" * 60)
    # Show a subset that fits in the terminal
    preview_cols = [
        "post_id", "engagement_rate", "total_interactions",
        "post_hour", "post_day_of_week", "is_weekend", "post_month",
        "word_count", "hashtag_count", "mention_count", "emoji_count",
        "rolling_avg_engagement", "days_since_last_post",
        "posting_frequency_7d", "sentiment_score",
    ]
    print(featured[preview_cols].to_string(index=False))

    print("\n" + "=" * 60)
    print("FEATURE REPORT")
    print("=" * 60)
    print(f"Rows:              {report.rows}")
    print(f"Original columns:  {len(report.original_columns)}")
    print(f"Final columns:     {len(report.final_columns)}")
    print(f"Features created:  {report.features_created}")
    print(f"\nActions ({len(report.actions)}):")
    for a in report.actions:
        print(f"  [{a.family:10s}] {a.column:25s} — {a.message}")

    print("\n" + "=" * 60)
    print("SAMPLE (first 3 rows of features)")
    print("=" * 60)
    for row in report.sample[:3]:
        print(row)