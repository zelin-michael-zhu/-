import pytest
from sqlalchemy import text

from app.core.database import engine


def test_database_connection():
    try:
        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1
    except Exception as exc:
        pytest.skip(f"Local MySQL is not available: {exc}")
