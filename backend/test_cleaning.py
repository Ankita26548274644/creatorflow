"""
Quick manual test for the cleaning module.
Run from backend/: python test_cleaning.py
"""
import pandas as pd
from app.services.cleaning import clean_dataframe


def make_messy_df():
    return pd.DataFrame({
        "post_id": [1, 2, 2, 3, 4, 5],              # duplicate post_id=2
        "date": ["2024-01-01", "2024-01-02", "2024-01-02",
                 "not-a-date", "2024-01-05", "2024-01-06"],
        "caption": ["  Hello   world  ", "Good morning",
                    "Good morning", None, "Late night", "  "],
        "likes": [10, 20, 20, 30, None, 40],
        "comments": [1, 2, 2, 3, 4, 5],
        "shares": [0, 1, 1, 0, 2, 3],
        "impressions": [100, 200, 200, 300, 400, 500],
    })


if __name__ == "__main__":
    df = make_messy_df()
    print("=" * 60)
    print("BEFORE CLEANING")
    print("=" * 60)
    print(df)
    print(f"\nRows: {len(df)}, Nulls: {int(df.isnull().sum().sum())}")

    cleaned, report = clean_dataframe(df)

    print("\n" + "=" * 60)
    print("AFTER CLEANING")
    print("=" * 60)
    print(cleaned)
    print(f"\nRows: {len(cleaned)}, Nulls: {int(cleaned.isnull().sum().sum())}")

    print("\n" + "=" * 60)
    print("CLEANING REPORT")
    print("=" * 60)
    print(f"Original rows: {report.original_rows}")
    print(f"Final rows:    {report.final_rows}")
    print(f"Rows removed:  {report.rows_removed}")
    print(f"Rows modified: {report.rows_modified}")
    print(f"Actions taken: {len(report.actions)}")
    for a in report.actions:
        print(f"  [{a.action}] {a.message}")