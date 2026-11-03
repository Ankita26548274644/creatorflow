"""
Feature engineering service for CreatorFlow.

Takes a cleaned DataFrame and derives:
    - Engagement features
    - Temporal features
    - Content features
    - Historical features
    - Sentiment features (VADER)
"""
import re
import pandas as pd
import numpy as np
from typing import Tuple, List

from app.schemas.features import FeatureReport, FeatureAction

# ---------------------------------------------------------------------------
# Optional VADER import — falls back gracefully if vaderSentiment isn't installed
# ---------------------------------------------------------------------------
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_AVAILABLE = True
    _vader = SentimentIntensityAnalyzer()
except ImportError:
    _VADER_AVAILABLE = False
    _vader = None


# Regex patterns for content features
HASHTAG_RE = re.compile(r"#\w+")
MENTION_RE = re.compile(r"@\w+")
URL_RE = re.compile(r"https?://\S+")
EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "]+",
    flags=re.UNICODE,
)


# ---------------------------------------------------------------------------
# E1 — Engagement features
# ---------------------------------------------------------------------------

def _add_engagement_features(df: pd.DataFrame, actions: List[FeatureAction]) -> pd.DataFrame:
    """Engagement rate and interaction totals."""
    total_interactions = (
        df.get("likes", 0) + df.get("comments", 0) + df.get("shares", 0)
    )
    safe_impressions = df["impressions"].replace(0, np.nan)

    df["total_interactions"] = total_interactions.fillna(0).astype(int)
    df["engagement_rate"] = (total_interactions / safe_impressions).fillna(0.0)

    actions.append(FeatureAction(
        family="engagement",
        column="total_interactions",
        message="Added total_interactions = likes + comments + shares.",
    ))
    actions.append(FeatureAction(
        family="engagement",
        column="engagement_rate",
        message="Added engagement_rate = total_interactions / impressions.",
    ))
    return df


# ---------------------------------------------------------------------------
# E2 — Temporal features
# ---------------------------------------------------------------------------

def _add_temporal_features(df: pd.DataFrame, actions: List[FeatureAction]) -> pd.DataFrame:
    """Hour, weekday, weekend flag, month, week of year."""
    if "date" not in df.columns:
        return df

    dates = pd.to_datetime(df["date"], errors="coerce")

    df["post_hour"] = dates.dt.hour
    df["post_day_of_week"] = dates.dt.dayofweek           # 0=Monday, 6=Sunday
    df["is_weekend"] = df["post_day_of_week"].isin([5, 6]).astype(int)
    df["post_month"] = dates.dt.month
    df["post_week_of_year"] = dates.dt.isocalendar().week.astype("Int64")

    for col, msg in [
        ("post_hour", "Extracted hour of day from date."),
        ("post_day_of_week", "Extracted day of week (0=Mon, 6=Sun)."),
        ("is_weekend", "Flagged weekend posts (Sat/Sun)."),
        ("post_month", "Extracted month from date."),
        ("post_week_of_year", "Extracted ISO week of year from date."),
    ]:
        actions.append(FeatureAction(
            family="temporal", column=col, message=msg,
        ))
    return df


# ---------------------------------------------------------------------------
# E3 — Content features
# ---------------------------------------------------------------------------

def _count_matches(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text or ""))


def _add_content_features(df: pd.DataFrame, actions: List[FeatureAction]) -> pd.DataFrame:
    """Caption length, word count, hashtags, mentions, URLs, emojis."""
    if "caption" not in df.columns:
        return df

    captions = df["caption"].fillna("").astype(str)

    df["caption_length"] = captions.str.len()
    df["word_count"] = captions.str.split().apply(len)
    df["hashtag_count"] = captions.apply(lambda c: _count_matches(HASHTAG_RE, c))
    df["mention_count"] = captions.apply(lambda c: _count_matches(MENTION_RE, c))
    df["url_count"] = captions.apply(lambda c: _count_matches(URL_RE, c))
    df["emoji_count"] = captions.apply(lambda c: _count_matches(EMOJI_RE, c))

    for col in [
        "caption_length", "word_count", "hashtag_count",
        "mention_count", "url_count", "emoji_count",
    ]:
        actions.append(FeatureAction(
            family="content", column=col,
            message=f"Added {col} from caption.",
        ))
    return df


# ---------------------------------------------------------------------------
# E4 — Historical features
# ---------------------------------------------------------------------------

def _add_historical_features(df: pd.DataFrame, actions: List[FeatureAction]) -> pd.DataFrame:
    """Rolling average engagement, posting frequency, days since last post."""
    if "date" not in df.columns or "engagement_rate" not in df.columns:
        return df

    df = df.sort_values("date").reset_index(drop=True)

    # Rolling average of engagement rate over the prior 5 posts (excludes current)
    df["rolling_avg_engagement"] = (
        df["engagement_rate"].shift(1).rolling(window=5, min_periods=1).mean().fillna(0.0)
    )

    # Days since last post
    df["days_since_last_post"] = (
        df["date"].diff().dt.days.fillna(0).astype(int)
    )

    # Posting frequency: posts in the trailing 7 days (excluding current)
    df["posting_frequency_7d"] = (
        df.set_index("date")
          .rolling("7D")["post_id"]
          .count()
          .shift(1)
          .fillna(0)
          .astype(int)
          .values
    )

    for col in [
        "rolling_avg_engagement", "days_since_last_post", "posting_frequency_7d",
    ]:
        actions.append(FeatureAction(
            family="historical", column=col,
            message=f"Added {col}.",
        ))
    return df


# ---------------------------------------------------------------------------
# E5 — Sentiment features
# ---------------------------------------------------------------------------

def _vader_score(text: str) -> float:
    if not _VADER_AVAILABLE or not text:
        return 0.0
    return _vader.polarity_scores(str(text))["compound"]


def _add_sentiment_features(df: pd.DataFrame, actions: List[FeatureAction]) -> pd.DataFrame:
    """VADER compound score on captions."""
    if "caption" not in df.columns:
        return df

    df["sentiment_score"] = df["caption"].fillna("").apply(_vader_score)

    actions.append(FeatureAction(
        family="sentiment",
        column="sentiment_score",
        message=(
            "Added VADER compound sentiment score."
            if _VADER_AVAILABLE
            else "VADER not installed — sentiment_score set to 0.0. "
                 "Run: pip install vaderSentiment"
        ),
    ))
    return df


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, FeatureReport]:
    """
    Run all feature-engineering steps and return (featured_df, report).
    Input df should be cleaned (from clean_dataframe).
    """
    actions: List[FeatureAction] = []
    original_columns = list(df.columns)

    df = _add_engagement_features(df, actions)
    df = _add_temporal_features(df, actions)
    df = _add_content_features(df, actions)
    df = _add_historical_features(df, actions)
    df = _add_sentiment_features(df, actions)

    final_columns = list(df.columns)

    # Sample for preview (first 5 rows, only feature columns)
    feature_cols = [
        c for c in final_columns
        if c not in {"post_id", "date", "caption", "hashtags"}
    ]
    sample_df = df[feature_cols].head(5).copy()
    sample = sample_df.to_dict(orient="records")

    # Replace NaN with None so JSON serialization works
    for row in sample:
        for k, v in row.items():
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                row[k] = None
            elif isinstance(v, (np.integer,)):
                row[k] = int(v)
            elif isinstance(v, (np.floating,)):
                row[k] = float(v)

    report = FeatureReport(
        original_columns=original_columns,
        final_columns=final_columns,
        rows=len(df),
        features_created=len(final_columns) - len(original_columns),
        actions=actions,
        sample=sample,
    )
    return df, report


# Expose for tests
VADER_AVAILABLE = _VADER_AVAILABLE