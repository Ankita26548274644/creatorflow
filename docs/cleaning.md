# Data Cleaning — CreatorFlow

## Purpose
Transforms a validated DataFrame into a clean one, ready for feature engineering.

## Rules (applied in order)

| Order | Rule | Effect |
|---|---|---|
| 1 | Deduplicate by `post_id` | Keeps first occurrence; drops rest |
| 2 | Fill missing numerics with 0 | Applies to `likes`, `comments`, `shares`, `impressions` |
| 3 | Fill missing captions with "" + indicator | Adds `caption_missing` column |
| 4 | Drop rows with unparseable dates | Protects temporal features |
| 5 | Normalize whitespace in captions | Trim + collapse internal runs |
| 6 | Standardize date dtype to datetime64 | Guarantees downstream compatibility |

## Output
`(cleaned_df, CleaningReport)` where the report contains:
- `original_rows`, `final_rows`
- `rows_removed`, `rows_modified`
- `actions`: list of `{action, column, affected_rows, message}`

## Action Codes
`REMOVED_DUPLICATES`, `FILLED_MISSING_WITH_ZERO`, `FILLED_MISSING_CAPTION`,
`DROPPED_UNPARSEABLE_DATE`, `NORMALIZED_TEXT`, `STANDARDIZED_DATE`