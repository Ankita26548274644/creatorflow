"""
Integration tests for the FastAPI endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "creatorflow_dev_key"}


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_validate_requires_api_key():
    res = client.post("/api/validate")
    assert res.status_code == 401


def test_validate_rejects_non_csv():
    files = {"file": ("test.txt", b"hello", "text/plain")}
    res = client.post("/api/validate", files=files, headers=HEADERS)
    assert res.status_code == 400


def test_validate_accepts_valid_csv(valid_csv_bytes):
    files = {"file": ("valid.csv", valid_csv_bytes, "text/csv")}
    res = client.post("/api/validate", files=files, headers=HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["passed"] is True
    assert body["prediction_enabled"] is True
    assert body["total_rows"] == 150


def test_upload_returns_all_three_blocks(valid_csv_bytes):
    files = {"file": ("valid.csv", valid_csv_bytes, "text/csv")}
    res = client.post("/api/upload", files=files, headers=HEADERS)
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "success"
    assert "validation" in body
    assert "cleaning" in body
    assert "features" in body
    assert body["validation"]["passed"] is True
    assert body["cleaning"]["final_rows"] == 150
    assert body["features"]["features_created"] > 0