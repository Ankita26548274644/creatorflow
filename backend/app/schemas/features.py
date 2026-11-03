from pydantic import BaseModel
from typing import List, Dict, Any


class FeatureAction(BaseModel):
    """A single feature-engineering action."""
    family: str          # "engagement" | "temporal" | "content" | "historical" | "sentiment"
    column: str          # the derived column name
    message: str


class FeatureReport(BaseModel):
    """Summary of all feature engineering operations."""
    original_columns: List[str]
    final_columns: List[str]
    rows: int
    features_created: int
    actions: List[FeatureAction] = []
    sample: List[Dict[str, Any]] = []   # first 5 rows, for preview