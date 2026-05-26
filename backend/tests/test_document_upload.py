import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.scripts.seed_demo_data import seed_demo_data
from main import app


def _client_or_skip():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"Local MySQL is not available: {exc}")
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    return TestClient(app)


def test_document_upload_creates_ready_record_and_file():
    client = _client_or_skip()
    response = client.post(
        "/api/documents/upload",
        data={"applicant_id": "1", "document_type": "CV", "notes": "test upload"},
        files={"file": ("cv.pdf", b"%PDF-1.4\nhello", "application/pdf")},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["type"] == "CV"
    assert payload["file_exists"] is True
    assert payload["original_filename"] == "cv.pdf"
