import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.scripts.seed_demo_data import seed_demo_data
from main import app


def test_profile_to_dashboard_interaction_flow():
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
    applicant = client.get("/api/applicants/default").json()
    applicant_id = applicant["id"]

    profile_response = client.put(
        f"/api/applicants/{applicant_id}",
        json={
            "full_name": applicant["full_name"],
            "email": applicant["email"],
            "university": applicant["university"],
            "major": "Business Analytics",
            "gpa_value": 3.7,
            "gpa_scale": 4.0,
            "ielts": 7.5,
            "target_countries_json": '["Hong Kong","Singapore"]',
            "target_fields_json": '["Business Analytics","Finance"]',
            "experiences_json": '["Analytics internship"]',
        },
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["gpa_converted_4"] == 3.7

    analysis_response = client.post(f"/api/applicants/{applicant_id}/analyze")
    assert analysis_response.status_code == 200
    assert analysis_response.json()["profile_strength_score"] > 0

    match_response = client.post(f"/api/matches/generate/{applicant_id}")
    assert match_response.status_code == 200
    matches = match_response.json()["items"]
    assert matches

    program_id = matches[0]["program"]["id"]
    application_response = client.post("/api/applications", json={"applicant_id": applicant_id, "program_id": program_id})
    assert application_response.status_code == 200
    assert application_response.json()["program_id"] == program_id

    checklist_response = client.post(f"/api/documents/checklist/{program_id}", json={"applicant_id": applicant_id})
    assert checklist_response.status_code == 200
    assert "missing_documents" in checklist_response.json()

    dashboard_response = client.get(f"/api/dashboard/{applicant_id}")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["stats"]["matched_programs"] >= 1
    assert dashboard["stats"]["applications"] >= 1

    task_response = client.post(
        "/api/browser-agent/start-task",
        json={"applicant_id": applicant_id, "program_id": program_id, "executor_type": "mock"},
    )
    assert task_response.status_code == 200
    task = task_response.json()
    assert task["applicant_id"] == applicant_id
    assert "load_context" in task["logs_json"]
