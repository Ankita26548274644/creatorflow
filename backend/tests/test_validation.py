"""
Unit tests for app.services.validation
"""
from app.services.validation import (
    validate_columns,
    validate_numeric_columns,
    validate_date_column,
    validate_implausible_values,
    validate_row_count,
    validate_dataframe,
    read_csv_safely,
    MIN_ROWS_FOR_PREDICTION,
    MIN_ROWS_HARD_FLOOR,
)
from io import BytesIO
import pandas as pd


# ---------- Column validation ----------

def test_missing_columns_are_reported(missing_column_df):
    issues = validate_columns(missing_column_df)
    codes = [i.code for i in issues]
    assert "MISSING_COLUMN" in codes
    # All 5 missing required columns should appear
    missing_cols = {i.column for i in issues if i.code == "MISSING_COLUMN"}
    assert "date" in missing_cols
    assert "likes" in missing_cols
    assert "comments" in missing_cols
    assert "shares" in missing_cols
    assert "impressions" in missing_cols


def test_extra_columns_produce_warnings(missing_column_df):
    # Add an extra column
    df = missing_column_df.copy()
    df["extra"] = "x"
    issues = validate_columns(df)
    warnings = [i for i in issues if i.severity == "warning"]
    assert any(i.code == "EXTRA_COLUMN" and i.column == "extra" for i in warnings)


def test_valid_columns_produce_no_errors(valid_dataframe):
    issues = validate_columns(valid_dataframe)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == []


# ---------- Numeric validation ----------

def test_negative_likes_are_errors(negative_likes_df):
    issues = validate_numeric_columns(negative_likes_df)
    assert any(i.code == "NEGATIVE_VALUE" and i.column == "likes" for i in issues)


def test_non_numeric_values_are_errors():
    df = pd.DataFrame({
        "post_id": [1, 2],
        "date": ["2024-01-01"] * 2,
        "caption": ["a", "b"],
        "likes": ["10", "abc"],
        "comments": [1, 2],
        "shares": [0, 0],
        "impressions": [100, 200],
    })
    issues = validate_numeric_columns(df)
    assert any(i.code == "NON_NUMERIC" and i.column == "likes" for i in issues)


def test_valid_numeric_produces_no_issues(valid_dataframe):
    issues = validate_numeric_columns(valid_dataframe)
    assert issues == []


# ---------- Date validation ----------

def test_bad_date_is_reported(bad_date_df):
    issues = validate_date_column(bad_date_df)
    assert any(i.code == "UNPARSEABLE_DATE" for i in issues)


def test_valid_dates_produce_no_issues(valid_dataframe):
    issues = validate_date_column(valid_dataframe)
    assert issues == []


# ---------- Implausibility ----------

def test_likes_greater_than_impressions_warning(implausible_df):
    issues = validate_implausible_values(implausible_df)
    assert any(i.code == "IMPLAUSIBLE_ENGAGEMENT" for i in issues)


def test_implausible_warning_is_only_warning(implausible_df):
    issues = validate_implausible_values(implausible_df)
    assert all(i.severity == "warning" for i in issues)


# ---------- Row count ----------

def test_too_few_rows_error(too_few_rows_df):
    issues = validate_row_count(too_few_rows_df)
    assert any(i.code == "TOO_FEW_ROWS" for i in issues)


def test_below_prediction_threshold_warning(valid_dataframe):
    # Slice down to 50 rows (between hard floor and prediction threshold)
    df = valid_dataframe.head(50)
    issues = validate_row_count(df)
    assert any(i.code == "BELOW_PREDICTION_THRESHOLD" for i in issues)
    assert not any(i.code == "TOO_FEW_ROWS" for i in issues)


def test_enough_rows_produces_no_issues(valid_dataframe):
    issues = validate_row_count(valid_dataframe)
    assert issues == []


# ---------- Reader ----------

def test_empty_bytes_produce_empty_file_error():
    df, issues = read_csv_safely(b"")
    assert df.empty
    assert any(i.code == "EMPTY_FILE" for i in issues)


def test_garbage_bytes_produce_parse_error():
    df, issues = read_csv_safely(b"\x00\x01\x02not a real csv at all\xff\xfe")
    # Should return some error — either EMPTY_FILE or PARSE_ERROR
    assert len(issues) > 0


# ---------- Full orchestrator ----------

def test_validate_dataframe_pass(valid_dataframe):
    report = validate_dataframe(valid_dataframe, "valid.csv")
    assert report.passed is True
    assert report.prediction_enabled is True
    assert report.errors == []
    assert report.warnings == []
    assert report.total_rows == 150
    assert report.total_columns == 7


def test_validate_dataframe_fail_multiple_issues(negative_likes_df):
    report = validate_dataframe(negative_likes_df, "bad.csv")
    assert report.passed is False
    codes = {i.code for i in report.errors}
    assert "NEGATIVE_VALUE" in codes