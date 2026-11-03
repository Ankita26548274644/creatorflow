from pydantic import BaseModel
from typing import List, Optional


class ValidationIssue(BaseModel):
    """A single problem found in the uploaded file."""
    code: str                    # machine-readable code, e.g. "MISSING_COLUMN"
    severity: str                # "error" | "warning"
    column: Optional[str] = None # which column it applies to, if any
    row: Optional[int] = None    # row index (0-based, excluding header), if any
    message: str                 # human-readable description


class ValidationReport(BaseModel):
    """Full response for a validation run."""
    filename: str
    total_rows: int
    total_columns: int
    passed: bool                 # True if no error-level issues
    prediction_enabled: bool     # True if row count >= MIN_ROWS_FOR_PREDICTION
    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []
    column_summary: dict = {}    # per-column dtype, null count, etc.