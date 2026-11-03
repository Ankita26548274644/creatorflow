"""
Unit tests for app.services.cleaning
"""
import pandas as pd
from app.services.cleaning import clean_dataframe


def make_df(**overrides):
    base = {
        "post_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "date": pd.to_datetime(["2024-01-01"] * 10),
        "caption": ["hello"] * 10,
        "likes": [10] * 10,
        "comments": [1] * 10,
        "shares": [0] * 10,
        "impressions": [100] * 10,
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_duplicates_are_removed():
    df = make_df()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    cleaned, report = clean_dataframe(df)
    assert len(cleaned) == 10
    assert any(a.action == "REMOVED_DUPLICATES" for a in report.actions)


def test_missing_numeric_filled_with_zero():
    df = make_df()
    df.loc[0, "likes"] = None
    cleaned, report = clean_dataframe(df)
    assert cleaned.loc[0, "likes"] == 0
    assert any(a.action == "FILLED_MISSING_WITH_ZERO" and a.column == "likes"
               for a in report.actions)


def test_missing_caption_gets_indicator_flag():
    df = make_df()
    df.loc[0, "caption"] = None
    cleaned, report = clean_dataframe(df)
    assert cleaned.loc[0, "caption"] == ""
    assert cleaned.loc[0, "caption_missing"] == 1
    assert any(a.action == "FILLED_MISSING_CAPTION" for a in report.actions)


def test_unparseable_dates_are_dropped():
    df = make_df()
    # Convert date column back to object dtype so we can inject a bad string
    df["date"] = df["date"].astype(str)
    df.loc[0, "date"] = "not-a-date"
    cleaned, report = clean_dataframe(df)
    assert len(cleaned) == 9
    assert any(a.action == "DROPPED_UNPARSEABLE_DATE" for a in report.actions)


def test_text_is_trimmed():
    df = make_df()
    df.loc[0, "caption"] = "  hello   world  "
    cleaned, report = clean_dataframe(df)
    assert cleaned.loc[0, "caption"] == "hello world"
    assert any(a.action == "NORMALIZED_TEXT" for a in report.actions)


def test_clean_dataframe_report_counts():
    df = make_df()
    df.loc[0, "likes"] = None
    df.loc[1, "caption"] = None
    cleaned, report = clean_dataframe(df)
    assert report.original_rows == 10
    assert report.final_rows == 10
    assert report.rows_removed == 0
    assert report.rows_modified >= 2