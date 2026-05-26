from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.portal_assistant import PortalSessionRequest, PortalSnapshotRequest, StartPortalSessionRequest
from app.services.portal_assistant.portal_assistant_service import PortalAssistantService, serialize_session

router = APIRouter(prefix="/portal-assistant", tags=["portal-assistant"])


@router.post("/start")
def start(payload: StartPortalSessionRequest, db: Session = Depends(get_db)):
    return PortalAssistantService(db).start(
        applicant_id=payload.applicant_id,
        program_id=payload.program_id,
        portal_url=payload.portal_url,
        executor_type=payload.executor_type,
        snapshot_text=payload.snapshot_text,
    )


@router.post("/user-logged-in")
def user_logged_in(payload: PortalSnapshotRequest, db: Session = Depends(get_db)):
    return PortalAssistantService(db).user_logged_in(payload.session_id, payload.snapshot_text)


@router.post("/generate-fill-plan")
def generate_fill_plan(payload: PortalSnapshotRequest, db: Session = Depends(get_db)):
    return PortalAssistantService(db).generate_fill_plan(payload.session_id, payload.snapshot_text)


@router.post("/run-fill-step")
def run_fill_step(payload: PortalSessionRequest, db: Session = Depends(get_db)):
    return PortalAssistantService(db).run_fill_step(payload.session_id)


@router.post("/approve-action")
def approve_first_medium_action(payload: PortalSessionRequest, db: Session = Depends(get_db)):
    service = PortalAssistantService(db)
    pending = service.list_pending_actions(payload.session_id)["items"]
    medium = next((item for item in pending if item["risk_level"] == "medium" and item["status"] == "pending"), None)
    if not medium:
        return {"session_id": payload.session_id, "message": "No pending medium-risk action requires approval."}
    return service.approve_action(medium["id"])


@router.post("/stop")
def stop(payload: PortalSessionRequest, db: Session = Depends(get_db)):
    return PortalAssistantService(db).stop(payload.session_id)


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    service = PortalAssistantService(db)
    return serialize_session(service._get_session(session_id))


@router.get("/logs")
def logs(session_id: int = Query(...), db: Session = Depends(get_db)):
    return PortalAssistantService(db).get_logs(session_id)


@router.get("/pending-actions")
def pending_actions(session_id: int = Query(...), db: Session = Depends(get_db)):
    return PortalAssistantService(db).list_pending_actions(session_id)


@router.post("/actions/{action_id}/approve")
def approve_action(action_id: int, db: Session = Depends(get_db)):
    return PortalAssistantService(db).approve_action(action_id)


@router.post("/actions/{action_id}/reject")
def reject_action(action_id: int, db: Session = Depends(get_db)):
    return PortalAssistantService(db).reject_action(action_id)


@router.post("/actions/{action_id}/mark-user-completed")
def mark_user_completed(action_id: int, db: Session = Depends(get_db)):
    return PortalAssistantService(db).mark_user_completed(action_id)


@router.post("/actions/{action_id}/execute")
def execute_action(action_id: int, db: Session = Depends(get_db)):
    return PortalAssistantService(db).execute_action(action_id)
