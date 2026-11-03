# Sample Data for CreatorFlow Demo

## Files

### valid_150.csv
- 150 rows, all required columns
- All numeric values non-negative
- All dates parseable as YYYY-MM-DD
- No implausible values
- **Expected validation result:** PASSED, prediction enabled

### partially_invalid.csv
- 7 rows
- Contains multiple deliberate errors:
  - Row 2: negative likes
  - Row 3: unparseable date
  - Row 4: likes > impressions (implausible)
  - Row 5: missing likes
- Only 7 rows, below the hard floor of 10
- **Expected validation result:** FAILED with 4 errors + 1 warning

### fully_invalid.csv
- 3 rows, wrong schema entirely
- Has columns: name, text, score
- Missing all 7 required columns
- **Expected validation result:** FAILED with 7 MISSING_COLUMN errors + 3 EXTRA_COLUMN warnings + 1 TOO_FEW_ROWS error