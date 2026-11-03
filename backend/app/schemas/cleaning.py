from pydantic import BaseModel
from typing import List


class CleaningAction(BaseModel):
    """A single cleaning action taken on the DataFrame."""
    action: str          # e.g., "REMOVED_DUPLICATES", "FILLED_MISSING"
    column: str | None = None
    affected_rows: int
    message: str


class CleaningReport(BaseModel):
    """Summary of all cleaning operations."""
    original_rows: int
    final_rows: int
    rows_removed: int
    rows_modified: int
    actions: List[CleaningAction] = []