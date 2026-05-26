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


def test_dashboard_and_browser_agent_include_document_context():
    client = _client_or_skip()
    before = client.get("/api/dashboard/1").json()["stats"]["missing_documents"]
    upload = client.post(
        "/api/documents/upload",
        data={"applicant_id": "1", "document_type": "Transcript"},
        files={"file": ("transcript.pdf", b"%PDF-1.4\ntranscript", "application/pdf")},
    )
    assert upload.status_code == 200
    after = client.get("/api/dashboard/1").json()["stats"]["missing_documents"]
    assert after <= before

    task = client.post("/api/browser-agent/start-task", json={"applicant_id": 1, "program_id": 1, "executor_type": "mock"})
    assert task.status_code == 200
    logs = task.json()["logs_json"]
    assert "documents" in logs
    assert "Transcript" in logs
