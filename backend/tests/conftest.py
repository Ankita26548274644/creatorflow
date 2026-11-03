"""
Shared pytest fixtures for CreatorFlow backend tests.
"""
import pytest
import pandas as pd
from io import BytesIO


@pytest.fixture
def valid_dataframe():
    """A clean 150-row DataFrame that should pass all validation."""
    import random
    from datetime import datetime, timedelta

    random.seed(42)
    start = datetime(2024, 1, 1)
    rows = []
    for i in range(1, 151):
        date = start + timedelta(days=i)
        likes = random.randint(20, 800)
        rows.append({
            "post_id": i,
            "date": date.strftime("%Y-%m-%d"),
            "caption": f"Sample caption {i}",
            "likes": likes,
            "comments": random.randint(1, 80),
            "shares": random.randint(0, 40),
            "impressions": likes * random.randint(4, 15),
        })
    return pd.DataFrame(rows)


@pytest.fixture
def missing_column_df():
    """Missing required columns — should produce MISSING_COLUMN errors."""
    return pd.DataFrame({
        "post_id": [1, 2, 3],
        "caption": ["a", "b", "c"],
    })


@pytest.fixture
def negative_likes_df():
    """Has a negative likes value — should produce NEGATIVE_VALUE."""
    return pd.DataFrame({
        "post_id": list(range(1, 21)),
        "date": ["2024-01-01"] * 20,
        "caption": ["test"] * 20,
        "likes": [10] * 19 + [-5],
        "comments": [1] * 20,
        "shares": [0] * 20,
        "impressions": [100] * 20,
    })


@pytest.fixture
def bad_date_df():
    """Has an unparseable date — should produce UNPARSEABLE_DATE."""
    return pd.DataFrame({
        "post_id": list(range(1, 21)),
        "date": ["2024-01-01"] * 19 + ["not-a-date"],
        "caption": ["test"] * 20,
        "likes": [10] * 20,
        "comments": [1] * 20,
        "shares": [0] * 20,
        "impressions": [100] * 20,
    })


@pytest.fixture
def too_few_rows_df():
    """Only 5 rows — should produce TOO_FEW_ROWS."""
    return pd.DataFrame({
        "post_id": [1, 2, 3, 4, 5],
        "date": ["2024-01-01"] * 5,
        "caption": ["test"] * 5,
        "likes": [10] * 5,
        "comments": [1] * 5,
        "shares": [0] * 5,
        "impressions": [100] * 5,
    })


@pytest.fixture
def implausible_df():
    """Has likes > impressions — should produce IMPLAUSIBLE_ENGAGEMENT warning."""
    return pd.DataFrame({
        "post_id": list(range(1, 21)),
        "date": ["2024-01-01"] * 20,
        "caption": ["test"] * 20,
        "likes": [100] * 20,
        "comments": [1] * 20,
        "shares": [0] * 20,
        "impressions": [50] * 20,
    })


@pytest.fixture
def valid_csv_bytes(valid_dataframe):
    """Bytes of a clean CSV, suitable for upload testing."""
    buf = BytesIO()
    valid_dataframe.to_csv(buf, index=False)
    return buf.getvalue()