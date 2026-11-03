"""
Validation service for CreatorFlow CSV uploads.

Defines the required schema and runs structural + content validation.
"""

REQUIRED_COLUMNS = [
    "post_id",
    "date",
    "caption",
    "likes",
    "comments",
    "shares",
    "impressions",
]

NUMERIC_COLUMNS = ["likes", "comments", "shares", "impressions"]

DATE_COLUMN = "date"

TEXT_COLUMNS = ["caption"]

MIN_ROWS_FOR_PREDICTION = 100
MIN_ROWS_HARD_FLOOR = 10   # below this, the file is unusable even for analytics

import io
import pandas as pd
from typing import Tuple, List, Dict, Any
from app.schemas.validation import ValidationIssue, ValidationReport


def _issue(code: str, severity: str, message: str,
           column: str = None, row: int = None) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity,
                           column=column, row=row, message=message)


def read_csv_safely(file_bytes: bytes) -> Tuple[pd.DataFrame, List[ValidationIssue]]:
    """Read CSV from bytes; return (df, issues)."""
    issues: List[ValidationIssue] = []
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except pd.errors.EmptyDataError:
        issues.append(_issue("EMPTY_FILE", "error", "CSV file is empty."))
        return pd.DataFrame(), issues
    except pd.errors.ParserError as e:
        issues.append(_issue("PARSE_ERROR", "error",
                             f"Could not parse CSV: {e}"))
        return pd.DataFrame(), issues
    except Exception as e:
        issues.append(_issue("READ_ERROR", "error",
                             f"Unexpected error reading CSV: {e}"))
        return pd.DataFrame(), issues
    return df, issues


def validate_columns(df: pd.DataFrame) -> List[ValidationIssue]:
    """Check for missing or unexpected columns."""
    issues: List[ValidationIssue] = []
    present = set(df.columns)
    required = set(REQUIRED_COLUMNS)

    missing = required - present
    for col in sorted(missing):
        issues.append(_issue(
            "MISSING_COLUMN", "error",
            f"Required column '{col}' is missing.",
            column=col,
        ))

    extra = present - required
    for col in sorted(extra):
        issues.append(_issue(
            "EXTRA_COLUMN", "warning",
            f"Unexpected column '{col}' will be ignored.",
            column=col,
        ))
    return issues


def validate_numeric_columns(df: pd.DataFrame) -> List[ValidationIssue]:
    """Check that numeric columns are numeric and non-negative."""
    issues: List[ValidationIssue] = []
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue  # missing column already reported

        # Try to coerce to numeric
        coerced = pd.to_numeric(df[col], errors="coerce")
        non_numeric_mask = coerced.isna() & df[col].notna()
        if non_numeric_mask.any():
            bad_rows = df.index[non_numeric_mask].tolist()[:5]
            issues.append(_issue(
                "NON_NUMERIC", "error",
                f"Column '{col}' contains non-numeric values in "
                f"{non_numeric_mask.sum()} row(s), e.g. rows {bad_rows}.",
                column=col,
            ))

        # Non-negativity check on the coerced values
        negative_mask = coerced < 0
        if negative_mask.any():
            bad_rows = df.index[negative_mask].tolist()[:5]
            issues.append(_issue(
                "NEGATIVE_VALUE", "error",
                f"Column '{col}' has negative values in "
                f"{negative_mask.sum()} row(s), e.g. rows {bad_rows}.",
                column=col,
            ))
    return issues


def validate_date_column(df: pd.DataFrame) -> List[ValidationIssue]:
    """Check that the date column parses."""
    issues: List[ValidationIssue] = []
    if DATE_COLUMN not in df.columns:
        return issues

    parsed = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    bad_mask = parsed.isna() & df[DATE_COLUMN].notna()
    if bad_mask.any():
        bad_rows = df.index[bad_mask].tolist()[:5]
        issues.append(_issue(
            "UNPARSEABLE_DATE", "error",
            f"Column '{DATE_COLUMN}' has unparseable dates in "
            f"{bad_mask.sum()} row(s), e.g. rows {bad_rows}.",
            column=DATE_COLUMN,
        ))
    return issues


def validate_implausible_values(df: pd.DataFrame) -> List[ValidationIssue]:
    """Flag values that are suspicious (likes > impressions, etc.)."""
    issues: List[ValidationIssue] = []
    if "likes" not in df.columns or "impressions" not in df.columns:
        return issues

    likes = pd.to_numeric(df["likes"], errors="coerce")
    impressions = pd.to_numeric(df["impressions"], errors="coerce")
    mask = (likes > impressions) & impressions.notna() & likes.notna()
    if mask.any():
        bad_rows = df.index[mask].tolist()[:5]
        issues.append(_issue(
            "IMPLAUSIBLE_ENGAGEMENT", "warning",
            f"{mask.sum()} row(s) have likes > impressions "
            f"(possible data error), e.g. rows {bad_rows}.",
        ))
    return issues


def validate_row_count(df: pd.DataFrame) -> List[ValidationIssue]:
    """Enforce minimum row counts."""
    issues: List[ValidationIssue] = []
    n = len(df)
    if n < MIN_ROWS_HARD_FLOOR:
        issues.append(_issue(
            "TOO_FEW_ROWS", "error",
            f"Only {n} row(s) found. Minimum {MIN_ROWS_HARD_FLOOR} required.",
        ))
    elif n < MIN_ROWS_FOR_PREDICTION:
        issues.append(_issue(
            "BELOW_PREDICTION_THRESHOLD", "warning",
            f"Only {n} row(s). Analytics will work, "
            f"but prediction requires at least {MIN_ROWS_FOR_PREDICTION}.",
        ))
    return issues


def build_column_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Per-column summary for the report."""
    summary = {}
    for col in df.columns:
        summary[col] = {
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isna().sum()),
            "sample": [str(v) for v in df[col].dropna().head(3).tolist()],
        }
    return summary


def validate_dataframe(df: pd.DataFrame, filename: str) -> ValidationReport:
    """Run all checks and produce the final report."""
    all_issues: List[ValidationIssue] = []

    all_issues.extend(validate_columns(df))
    all_issues.extend(validate_numeric_columns(df))
    all_issues.extend(validate_date_column(df))
    all_issues.extend(validate_implausible_values(df))
    all_issues.extend(validate_row_count(df))

    errors = [i for i in all_issues if i.severity == "error"]
    warnings = [i for i in all_issues if i.severity == "warning"]

    return ValidationReport(
        filename=filename,
        total_rows=len(df),
        total_columns=len(df.columns),
        passed=len(errors) == 0,
        prediction_enabled=(len(df) >= MIN_ROWS_FOR_PREDICTION and len(errors) == 0),
        errors=errors,
        warnings=warnings,
        column_summary=build_column_summary(df),
    )