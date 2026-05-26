import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.models import Applicant
from app.scripts.seed_demo_data import seed_demo_data
from app.services.matching.gpa_converter import convert_to_4
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


def test_document_download_status_and_checklist_flow():
    client = _client_or_skip()
    db = SessionLocal()
    try:
        applicant = Applicant(
            full_name="Document Test",
            email=f"document-test-{uuid4().hex}@applypilot.local",
            major="Business Analytics",
            gpa_value=3.5,
            gpa_scale=4.0,
            gpa_converted_4=convert_to_4(3.5, 4.0),
        )
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
        applicant_id = applicant.id
    finally:
        db.close()
    upload = client.post(
        "/api/documents/upload",
        data={"applicant_id": str(applicant_id), "document_type": "CV"},
        files={"file": ("cv.pdf", b"%PDF-1.4\nhello", "application/pdf")},
    )
    assert upload.status_code == 200
    document_id = upload.json()["id"]

    download = client.get(f"/api/documents/{document_id}/download")
    assert download.status_code == 200
    assert download.content.startswith(b"%PDF")

    status = client.put(f"/api/documents/{document_id}/status", json={"status": "submitted"})
    assert status.status_code == 200
    assert status.json()["status"] == "submitted"

    checklist = client.post("/api/documents/checklist/1", json={"applicant_id": applicant_id})
    assert checklist.status_code == 200
    payload = checklist.json()
    submitted = [item["required"]["document_type"] for item in payload["submitted_documents"]]
    assert "CV" in submitted
    assert any(item["required"]["document_type"] == "Transcript" for item in payload["missing_documents"])


def test_document_missing_file_returns_404():
    client = _client_or_skip()
    response = client.get("/api/documents/999999/download")
    assert response.status_code == 404
