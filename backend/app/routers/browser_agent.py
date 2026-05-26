from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.browser_executor import ApproveActionRequest, StartBrowserTaskRequest, TaskIdRequest
from app.services.browser_agent.browser_agent_service import BrowserAgentService, get_opencli_status

router = APIRouter(prefix="/browser-agent", tags=["browser-agent"])


@router.get("/executors")
def executors(db: Session = Depends(get_db)):
    return BrowserAgentService(db).list_executors()


@router.get("/opencli/status")
def opencli_status():
    return get_opencli_status()


@router.post("/start-task")
def start_task(payload: StartBrowserTaskRequest, db: Session = Depends(get_db)):
    task = BrowserAgentService(db).start_task(payload.applicant_id, payload.program_id, payload.executor_type)
    return task


@router.post("/run-next-step")
def run_next_step(payload: TaskIdRequest, db: Session = Depends(get_db)):
    try:
        return BrowserAgentService(db).run_next_step(payload.task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/approve-action")
def approve_action(payload: ApproveActionRequest, db: Session = Depends(get_db)):
    try:
        return BrowserAgentService(db).approve_action(payload.task_id, payload.action_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/stop-task")
def stop_task(payload: TaskIdRequest, db: Session = Depends(get_db)):
    try:
        return BrowserAgentService(db).stop_task(payload.task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/logs")
def logs(task_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        return BrowserAgentService(db).get_logs(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
