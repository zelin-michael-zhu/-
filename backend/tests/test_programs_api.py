import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import engine
from main import app


def test_programs_api_returns_items_shape():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"Local MySQL is not available: {exc}")
    client = TestClient(app)
    response = client.get("/api/programs")
    assert response.status_code == 200
    payload = response.json()
    assert "total" in payload
    assert "items" in payload
