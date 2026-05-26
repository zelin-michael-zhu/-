import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.scripts.seed_demo_data import seed_demo_data
from main import app


def _client_ids():
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
    programs = client.get("/api/programs?limit=1").json()["items"]
    assert programs
    return client, applicant["id"], programs[0]["id"]


def _start_logged_in_plan(client: TestClient, applicant_id: int, program_id: int):
    started = client.post(
        "/api/portal-assistant/start",
        json={"applicant_id": applicant_id, "program_id": program_id, "executor_type": "mock", "portal_url": "https://example.edu/apply"},
    )
    assert started.status_code == 200
    session = started.json()
    assert session["status"] == "waiting_user_login"

    logged_in = client.post("/api/portal-assistant/user-logged-in", json={"session_id": session["id"], "snapshot_text": "application form"})
    assert logged_in.status_code == 200
    assert logged_in.json()["status"] == "logged_in"

    plan = client.post("/api/portal-assistant/generate-fill-plan", json={"session_id": session["id"], "snapshot_text": "application form"})
    assert plan.status_code == 200
    actions = plan.json()["items"]
    assert actions
    return session["id"], actions


def test_low_risk_action_auto_executes_and_writes_audit_log():
    client, applicant_id, program_id = _client_ids()
    session_id, actions = _start_logged_in_plan(client, applicant_id, program_id)

    low = next(item for item in actions if item["risk_level"] == "low" and item["action_type"] == "fill_field")
    executed = client.post(f"/api/portal-assistant/actions/{low['id']}/execute")
    assert executed.status_code == 200
    assert executed.json()["action"]["status"] == "executed"

    logs = client.get(f"/api/portal-assistant/logs?session_id={session_id}")
    assert logs.status_code == 200
    actions_logged = [item["action"] for item in logs.json()["logs"]]
    assert f"execute:{low['action_type']}" in actions_logged


def test_medium_risk_action_waits_for_approval_then_executes():
    client, applicant_id, program_id = _client_ids()
    _, actions = _start_logged_in_plan(client, applicant_id, program_id)
    medium = next(item for item in actions if item["risk_level"] == "medium")

    blocked_before_approval = client.post(f"/api/portal-assistant/actions/{medium['id']}/execute")
    assert blocked_before_approval.status_code == 400

    approved = client.post(f"/api/portal-assistant/actions/{medium['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    executed = client.post(f"/api/portal-assistant/actions/{medium['id']}/execute")
    assert executed.status_code == 200
    assert executed.json()["action"]["status"] == "executed"


def test_rejected_action_does_not_execute():
    client, applicant_id, program_id = _client_ids()
    _, actions = _start_logged_in_plan(client, applicant_id, program_id)
    low = next(item for item in actions if item["risk_level"] == "low" and item["status"] == "pending")

    rejected = client.post(f"/api/portal-assistant/actions/{low['id']}/reject")
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    executed = client.post(f"/api/portal-assistant/actions/{low['id']}/execute")
    assert executed.status_code == 400


def test_blocked_final_submit_never_executes():
    client, applicant_id, program_id = _client_ids()
    _, actions = _start_logged_in_plan(client, applicant_id, program_id)
    final_submit = next(item for item in actions if item["action_type"] == "final_submit")
    assert final_submit["blocked"] is True
    assert final_submit["status"] == "blocked"

    executed = client.post(f"/api/portal-assistant/actions/{final_submit['id']}/execute")
    assert executed.status_code == 400


def test_captcha_action_waits_for_user_and_mark_completed_resumes_workflow():
    client, applicant_id, program_id = _client_ids()
    started = client.post(
        "/api/portal-assistant/start",
        json={
            "applicant_id": applicant_id,
            "program_id": program_id,
            "executor_type": "mock",
            "portal_url": "https://example.edu/apply/captcha",
            "snapshot_text": "captcha verification page",
        },
    )
    assert started.status_code == 200
    session = started.json()
    assert session["status"] == "waiting_user_captcha"

    plan = client.post("/api/portal-assistant/generate-fill-plan", json={"session_id": session["id"], "snapshot_text": "captcha verification page"})
    assert plan.status_code == 200
    captcha = next(item for item in plan.json()["items"] if item["action_type"] == "solve_captcha")
    assert captcha["blocked"] is True

    completed = client.post(f"/api/portal-assistant/actions/{captcha['id']}/mark-user-completed")
    assert completed.status_code == 200
    assert completed.json()["status"] == "user_completed"

    refreshed = client.get(f"/api/portal-assistant/sessions/{session['id']}")
    assert refreshed.status_code == 200
    assert refreshed.json()["status"] == "logged_in"
