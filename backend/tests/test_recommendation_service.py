import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.scripts.seed_demo_data import seed_demo_data
from main import app


def test_mock_recommendation_includes_evidence_and_no_fabrication():
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
    client = TestClient(app)
    response = client.post("/api/recommendations/generate/1?provider=mock")
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendations"]
    first = payload["recommendations"][0]
    assert first["evidence"][0]["source_url"]
    assert first["evidence"][0]["text"]
    assert "Verify" in first["ai_reason"]
