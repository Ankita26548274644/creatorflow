"""
Data cleaning service for CreatorFlow.

Takes a validated DataFrame and produces a cleaned DataFrame plus a report
of every action taken.
"""
import pandas as pd
import numpy as np
from typing import Tuple, List

from app.schemas.cleaning import CleaningReport, CleaningAction
from app.services.validation import (
    NUMERIC_COLUMNS,
    DATE_COLUMN,
    TEXT_COLUMNS,
)

# Columns that must be present for cleaning to proceed
CLEANING_COLUMNS = ["post_id"] + NUMERIC_COLUMNS + [DATE_COLUMN] + TEXT_COLUMNS


# ---------------------------------------------------------------------------
# Individual cleaning steps
# ---------------------------------------------------------------------------

def _deduplicate(df: pd.DataFrame, actions: List[CleaningAction]) -> pd.DataFrame:
    """Remove duplicate rows by post_id (or full-row match if no post_id)."""
    original = len(df)

    if "post_id" in df.columns:
        df = df.drop_duplicates(subset=["post_id"], keep="first")
    else:
        df = df.drop_duplicates(keep="first")

    removed = original - len(df)
    if removed > 0:
        actions.append(CleaningAction(
            action="REMOVED_DUPLICATES",
            column="post_id" if "post_id" in df.columns else None,
            affected_rows=removed,
            message=f"Removed {removed} duplicate row(s).",
        ))
    return df


def _fill_missing_numeric(df: pd.DataFrame, actions: List[CleaningAction]) -> pd.DataFrame:
    """Fill missing numeric values with 0."""
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        missing = df[col].isna().sum()
        if missing > 0:
            df[col] = df[col].fillna(0)
            actions.append(CleaningAction(
                action="FILLED_MISSING_WITH_ZERO",
                column=col,
                affected_rows=int(missing),
                message=f"Filled {missing} missing value(s) in '{col}' with 0.",
            ))
    return df


def _fill_missing_captions(df: pd.DataFrame, actions: List[CleaningAction]) -> pd.DataFrame:
    """Replace missing captions with empty string + add an indicator column."""
    if "caption" not in df.columns:
        return df

    missing_mask = df["caption"].isna()
    missing_count = missing_mask.sum()

    if missing_count > 0:
        df["caption"] = df["caption"].fillna("")
        df["caption_missing"] = missing_mask.astype(int)
        actions.append(CleaningAction(
            action="FILLED_MISSING_CAPTION",
            column="caption",
            affected_rows=int(missing_count),
            message=(
                f"Replaced {missing_count} missing caption(s) with empty string; "
                f"added 'caption_missing' indicator column."
            ),
        ))
    else:
        if "caption_missing" not in df.columns:
            df["caption_missing"] = 0

    return df


def _drop_unparseable_dates(df: pd.DataFrame, actions: List[CleaningAction]) -> pd.DataFrame:
    """Drop rows where date can't be parsed."""
    if DATE_COLUMN not in df.columns:
        return df

    original = len(df)
    parsed = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    valid_mask = parsed.notna()

    df = df[valid_mask].copy()
    df[DATE_COLUMN] = parsed[valid_mask].values

    removed = original - len(df)
    if removed > 0:
        actions.append(CleaningAction(
            action="DROPPED_UNPARSEABLE_DATE",
            column=DATE_COLUMN,
            affected_rows=removed,
            message=f"Dropped {removed} row(s) with unparseable dates.",
        ))
    return df


def _normalize_text(df: pd.DataFrame, actions: List[CleaningAction]) -> pd.DataFrame:
    """Trim whitespace and normalize internal spacing in captions."""
    if "caption" not in df.columns:
        return df

    before = df["caption"].astype(str).copy()
    df["caption"] = df["caption"].astype(str).str.strip()
    df["caption"] = df["caption"].str.replace(r"\s+", " ", regex=True)

    changed = (before != df["caption"]).sum()
    if changed > 0:
        actions.append(CleaningAction(
            action="NORMALIZED_TEXT",
            column="caption",
            affected_rows=int(changed),
            message=f"Trimmed/normalized whitespace in {changed} caption(s).",
        ))
    return df


def _standardize_dates(df: pd.DataFrame, actions: List[CleaningAction]) -> pd.DataFrame:
    """Ensure the date column is a proper datetime64 dtype."""
    if DATE_COLUMN not in df.columns:
        return df

    if not pd.api.types.is_datetime64_any_dtype(df[DATE_COLUMN]):
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")

    actions.append(CleaningAction(
        action="STANDARDIZED_DATE",
        column=DATE_COLUMN,
        affected_rows=len(df),
        message="Standardized date column to datetime64.",
    ))
    return df


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
    """
    Run all cleaning steps in order and return (cleaned_df, report).
    Input df should already be validated (required columns present).
    """
    actions: List[CleaningAction] = []
    original_rows = len(df)

    # Order matters:
    # 1. Deduplicate first — cheaper on smaller data
    # 2. Fill missing numeric — before any row-dropping that depends on numerics
    # 3. Fill missing captions — before text normalization
    # 4. Drop bad dates — before standardizing
    # 5. Normalize text — after missing-caption handling
    # 6. Standardize dates — last, since we now have only valid dates

    df = _deduplicate(df, actions)
    df = _fill_missing_numeric(df, actions)
    df = _fill_missing_captions(df, actions)
    df = _drop_unparseable_dates(df, actions)
    df = _normalize_text(df, actions)
    df = _standardize_dates(df, actions)

    df = df.reset_index(drop=True)

    rows_modified = sum(
        a.affected_rows for a in actions
        if a.action.startswith("FILLED") or a.action.startswith("NORMALIZED")
    )

    report = CleaningReport(
        original_rows=original_rows,
        final_rows=len(df),
        rows_removed=original_rows - len(df),
        rows_modified=rows_modified,
        actions=actions,
    )
    return df, report