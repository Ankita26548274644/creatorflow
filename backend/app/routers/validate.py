from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header, status

from app.services.validation import read_csv_safely, validate_dataframe
from app.routers.upload import verify_api_key

router = APIRouter(prefix="/api", tags=["Validation"])


@router.post("/validate")
async def validate_csv(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_api_key),
):
    """
    Validate the structure and content of an uploaded CSV.
    Returns a structured validation report.
    Does NOT save the file — use /api/upload for persistence.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file received.")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are accepted for validation.",
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    df, read_issues = read_csv_safely(contents)

    # If reading itself failed, return early with a report
    if read_issues:
        from app.schemas.validation import ValidationReport
        return ValidationReport(
            filename=file.filename,
            total_rows=0,
            total_columns=0,
            passed=False,
            prediction_enabled=False,
            errors=read_issues,
            warnings=[],
            column_summary={},
        )

    report = validate_dataframe(df, file.filename)
    return report