from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import uuid
from pathlib import Path
from datetime import datetime

from app.config import settings
from app.services.validation import read_csv_safely, validate_dataframe
from app.services.cleaning import clean_dataframe
from app.services.features import engineer_features

router = APIRouter(prefix="/api", tags=["Upload"])

ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
}

ALLOWED_EXTENSION = ".csv"

DEV_API_KEY = "creatorflow_dev_key"


def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """Simple API key check. Will be replaced with JWT/OAuth later."""
    expected = getattr(settings, "API_KEY", DEV_API_KEY)
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key.",
        )
    return True


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_api_key),
):
    """
    Full pipeline:
        upload → validation → cleaning → feature engineering
    Returns metadata plus validation, cleaning, and feature summaries.
    """

    # ---- 1. File presence ----
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file received.")

    # ---- 2. Extension check ----
    original_name = file.filename
    ext = Path(original_name).suffix.lower()
    if ext != ALLOWED_EXTENSION:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{ext}'. Only .csv files are allowed.",
        )

    # ---- 3. MIME type check ----
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MIME type '{content_type}'. Expected a CSV file.",
        )

    # ---- 4. Size check ----
    contents = await file.read()
    size_bytes = len(contents)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if size_bytes == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File too large ({size_bytes / (1024 * 1024):.2f} MB). "
                f"Maximum allowed: {settings.MAX_UPLOAD_SIZE_MB} MB."
            ),
        )

    # ---- 5. Save with unique name ----
    upload_id = uuid.uuid4().hex
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{upload_id}.csv"

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / safe_name

    try:
        with open(saved_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save file: {str(e)}"
        )

    # ---- 6. Validation ----
    df, read_issues = read_csv_safely(contents)

    if read_issues:
        validation_summary = {
            "passed": False,
            "error_count": len(read_issues),
            "warning_count": 0,
            "prediction_enabled": False,
            "errors": [issue.model_dump() for issue in read_issues],
            "warnings": [],
        }
        cleaning_summary = None
        features_summary = None
    else:
        report = validate_dataframe(df, original_name)
        validation_summary = {
            "passed": report.passed,
            "error_count": len(report.errors),
            "warning_count": len(report.warnings),
            "prediction_enabled": report.prediction_enabled,
            "errors": [issue.model_dump() for issue in report.errors],
            "warnings": [issue.model_dump() for issue in report.warnings],
        }

        # ---- 6b. Cleaning (only if validation passed) ----
        if report.passed:
            cleaned_df, cleaning_report = clean_dataframe(df)
            cleaning_summary = {
                "original_rows": cleaning_report.original_rows,
                "final_rows": cleaning_report.final_rows,
                "rows_removed": cleaning_report.rows_removed,
                "rows_modified": cleaning_report.rows_modified,
                "actions": [a.model_dump() for a in cleaning_report.actions],
            }

            # ---- 6c. Feature engineering ----
            featured_df, features_report = engineer_features(cleaned_df)
            features_summary = {
                "rows": features_report.rows,
                "features_created": features_report.features_created,
                "final_columns": features_report.final_columns,
                "actions": [a.model_dump() for a in features_report.actions],
                "sample": features_report.sample,
            }
        else:
            cleaning_summary = None
            features_summary = None

    # ---- 7. Return ----
    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "upload_id": upload_id,
            "original_filename": original_name,
            "saved_filename": safe_name,
            "saved_path": str(saved_path.resolve()),
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 3),
            "content_type": content_type,
            "validation": validation_summary,
            "cleaning": cleaning_summary,
            "features": features_summary,
        },
    )