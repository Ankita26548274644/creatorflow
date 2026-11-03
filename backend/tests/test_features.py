"""
Unit tests for app.services.features
"""
import pandas as pd
from app.services.features import engineer_features, VADER_AVAILABLE


def make_clean_df():
    return pd.DataFrame({
        "post_id": [1, 2, 3, 4, 5],
        "date": pd.to_datetime([
            "2024-01-01 09:00", "2024-01-02 14:00", "2024-01-03 20:00",
            "2024-01-06 10:00", "2024-01-07 22:00",
        ]),
        "caption": [
            "Good morning #hello",
            "Check this @friend",
            "Simple post",
            "Weekend vibes #fun #sun",
            "Late night 😀",
        ],
        "likes": [10, 20, 30, 40, 50],
        "comments": [1, 2, 3, 4, 5],
        "shares": [0, 1, 2, 3, 4],
        "impressions": [100, 200, 300, 400, 500],
    })


def test_engagement_rate_computed():
    df = make_clean_df()
    featured, report = engineer_features(df)
    assert "engagement_rate" in featured.columns
    # Row 0: (10+1+0)/100 = 0.11
    assert abs(featured.loc[0, "engagement_rate"] - 0.11) < 1e-6


def test_total_interactions_computed():
    df = make_clean_df()
    featured, _ = engineer_features(df)
    # Row 0: 10+1+0 = 11
    assert featured.loc[0, "total_interactions"] == 11


def test_temporal_features_extracted():
    df = make_clean_df()
    featured, _ = engineer_features(df)
    assert featured.loc[0, "post_hour"] == 9
    # Jan 6, 2024 is a Saturday → day_of_week 5
    assert featured.loc[3, "post_day_of_week"] == 5
    assert featured.loc[3, "is_weekend"] == 1


def test_content_features():
    df = make_clean_df()
    featured, _ = engineer_features(df)
    assert featured.loc[0, "hashtag_count"] == 1
    assert featured.loc[1, "mention_count"] == 1
    assert featured.loc[3, "hashtag_count"] == 2
    # Row 4 has one emoji
    assert featured.loc[4, "emoji_count"] >= 1


def test_historical_features_present():
    df = make_clean_df()
    featured, _ = engineer_features(df)
    assert "rolling_avg_engagement" in featured.columns
    assert "days_since_last_post" in featured.columns
    assert "posting_frequency_7d" in featured.columns
    # First row has no prior posts, so days_since_last_post = 0
    assert featured.loc[0, "days_since_last_post"] == 0


def test_sentiment_score_range():
    df = make_clean_df()
    featured, _ = engineer_features(df)
    assert "sentiment_score" in featured.columns
    # All scores must be between -1 and 1
    assert featured["sentiment_score"].between(-1, 1).all()


def test_feature_report_shape():
    df = make_clean_df()
    featured, report = engineer_features(df)
    assert report.rows == 5
    assert report.features_created > 0
    assert len(report.sample) == 5
    assert len(report.actions) >= 10  # at least 10 features derived