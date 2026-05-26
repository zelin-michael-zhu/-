import json
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Applicant, AuditLog, PendingAction, PortalSession, Program
from app.services.agent_orchestrator.approval_gate import ApprovalGate, serialize_pending_action
from app.services.agent_orchestrator.audit_log_service import AuditLogService
from app.services.browser_agent.mock_executor import MockExecutor
from app.services.browser_agent.opencli_executor import OpenCLIExecutor
from app.services.browser_agent.playwright_executor import PlaywrightExecutor
from app.services.documents.document_service import DocumentService
from app.services.portal_assistant.portal_snapshot_parser import detects_captcha_or_login
from app.services.portal_assistant.portal_upload_planner import DOCUMENT_UPLOAD_TYPES


def _split_name(full_name: str | None) -> tuple[str, str]:
    parts = (full_name or "").strip().split(" ", 1)
    return (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")


def _preview(value: str | None) -> str | None:
    if value is None:
        return None
    return value[:20]


def serialize_session(session: PortalSession) -> dict:
    return {column.name: getattr(session, column.name) for column in session.__table__.columns}


def serialize_audit_log(log: AuditLog) -> dict:
    data = {column.name: getattr(log, column.name) for column in log.__table__.columns}
    if log.metadata_json:
        try:
            data["metadata"] = json.loads(log.metadata_json)
        except Exception:
            data["metadata"] = None
    return data


class PortalAssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditLogService(db)
        self.gate = ApprovalGate(db)

    def _get_session(self, session_id: int) -> PortalSession:
        session = self.db.get(PortalSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Portal session not found")
        return session

    def _get_executor(self, executor_type: str):
        if executor_type == "opencli":
            return OpenCLIExecutor()
        if executor_type == "playwright":
            return PlaywrightExecutor()
        return MockExecutor()

    def start(
        self,
        *,
        applicant_id: int,
        program_id: int | None,
        portal_url: str | None,
        executor_type: str = "mock",
        snapshot_text: str | None = None,
    ) -> dict:
        applicant = self.db.get(Applicant, applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")
        if program_id and not self.db.get(Program, program_id):
            raise HTTPException(status_code=404, detail="Program not found")

        inferred_snapshot = snapshot_text
        if not inferred_snapshot and portal_url and "captcha" in portal_url.lower():
            inferred_snapshot = "captcha verification page"
        login_detected, captcha_detected = detects_captcha_or_login(inferred_snapshot or "login page")
        status = "waiting_user_captcha" if captcha_detected else "waiting_user_login" if login_detected else "waiting_user_login"

        session = PortalSession(
            applicant_id=applicant_id,
            program_id=program_id,
            executor_type=executor_type or "mock",
            portal_url=portal_url,
            status=status,
            last_page_url=portal_url,
            last_snapshot_text=inferred_snapshot,
        )
        self.db.add(session)
        self.db.flush()
        self.audit.create(
            applicant_id=applicant_id,
            action="portal_session:start",
            actor="system",
            risk={"risk_level": "low", "requires_approval": False, "blocked": False},
            message="Portal assistant started. User must login and complete CAPTCHA manually.",
            metadata={"portal_session_id": session.id, "program_id": program_id, "executor_type": executor_type},
            commit=False,
        )
        self.db.commit()
        self.db.refresh(session)
        return serialize_session(session)

    def user_logged_in(self, session_id: int, snapshot_text: str | None = None) -> dict:
        session = self._get_session(session_id)
        if snapshot_text is not None:
            session.last_snapshot_text = snapshot_text
        _, captcha_detected = detects_captcha_or_login(session.last_snapshot_text)
        session.status = "waiting_user_captcha" if captcha_detected else "logged_in"
        self.audit.create(
            applicant_id=session.applicant_id,
            action="portal_session:user_logged_in",
            actor="user",
            risk={"risk_level": "low", "requires_approval": False, "blocked": False},
            approved_by_user=True,
            message="User confirmed portal login or manual verification progress.",
            metadata={"portal_session_id": session.id, "status": session.status},
            commit=False,
        )
        self.db.commit()
        self.db.refresh(session)
        return serialize_session(session)

    def generate_fill_plan(self, session_id: int, snapshot_text: str | None = None) -> dict:
        session = self._get_session(session_id)
        if snapshot_text is not None:
            session.last_snapshot_text = snapshot_text

        existing = self.list_pending_actions(session_id)
        if existing["items"]:
            return {"session": serialize_session(session), "items": existing["items"]}

        _, captcha_detected = detects_captcha_or_login(session.last_snapshot_text)
        if captcha_detected:
            session.status = "waiting_user_captcha"
            self.gate.propose(
                applicant_id=session.applicant_id,
                program_id=session.program_id,
                portal_session_id=session.id,
                action_type="solve_captcha",
                target_label="CAPTCHA",
                description="solve captcha",
            )
            self.db.commit()
            return {"session": serialize_session(session), "items": self.list_pending_actions(session_id)["items"]}

        applicant = self.db.get(Applicant, session.applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")
        first_name, last_name = _split_name(applicant.full_name)
        field_values = [
            ("first_name", "first name", first_name, "fill first name"),
            ("last_name", "last name", last_name, "fill last name"),
            ("email", "email", applicant.email, "fill email"),
            ("university", "university", applicant.university, "fill university"),
            ("major", "major", applicant.major, "fill major"),
            ("gpa", "GPA", str(applicant.gpa_converted_4 or applicant.gpa_value or ""), "fill GPA"),
        ]
        for selector, label, value, description in field_values:
            if value:
                self.gate.propose(
                    applicant_id=session.applicant_id,
                    program_id=session.program_id,
                    portal_session_id=session.id,
                    action_type="fill_field",
                    target_label=label,
                    target_selector=selector,
                    proposed_value=str(value),
                    description=description,
                )

        latest_docs = DocumentService(self.db).get_latest_documents_by_type(session.applicant_id)
        for doc_type in DOCUMENT_UPLOAD_TYPES:
            document = latest_docs.get(doc_type.lower())
            if document and document.status in {"ready", "submitted"} and document.file_path:
                self.gate.propose(
                    applicant_id=session.applicant_id,
                    program_id=session.program_id,
                    portal_session_id=session.id,
                    action_type="upload_document",
                    target_label=doc_type,
                    target_selector=f"upload_{doc_type.lower().replace(' ', '_')}",
                    proposed_value=document.file_path,
                    description=f"upload {doc_type} to draft",
                )
            else:
                self.gate.propose(
                    applicant_id=session.applicant_id,
                    program_id=session.program_id,
                    portal_session_id=session.id,
                    action_type="upload_document",
                    target_label=doc_type,
                    target_selector=f"upload_{doc_type.lower().replace(' ', '_')}",
                    proposed_value=None,
                    description=f"upload {doc_type} to draft",
                    force_blocked_reason=f"{doc_type} is missing or not ready. Upload it in Documents before portal upload.",
                )

        self.gate.propose(
            applicant_id=session.applicant_id,
            program_id=session.program_id,
            portal_session_id=session.id,
            action_type="save_draft",
            target_label="Save Draft",
            target_selector="button:save-draft",
            description="click save draft",
        )
        self.gate.propose(
            applicant_id=session.applicant_id,
            program_id=session.program_id,
            portal_session_id=session.id,
            action_type="send_recommender_invitation",
            target_label="Recommender invitation",
            target_selector="button:send-recommender-invitation",
            proposed_value="recommender@example.com",
            description="send recommender invitation",
        )
        self.gate.propose(
            applicant_id=session.applicant_id,
            program_id=session.program_id,
            portal_session_id=session.id,
            action_type="final_submit",
            target_label="Final Submit",
            target_selector="button:final-submit",
            description="final submit",
        )
        self.gate.propose(
            applicant_id=session.applicant_id,
            program_id=session.program_id,
            portal_session_id=session.id,
            action_type="payment",
            target_label="Application Fee",
            target_selector="button:payment",
            description="payment application fee",
        )
        session.status = "filling"
        self.db.commit()
        self.db.refresh(session)
        return {"session": serialize_session(session), "items": self.list_pending_actions(session_id)["items"]}

    def list_pending_actions(self, session_id: int) -> dict:
        rows = (
            self.db.query(PendingAction)
            .filter(PendingAction.portal_session_id == session_id)
            .order_by(PendingAction.id.asc())
            .all()
        )
        return {"session_id": session_id, "items": [serialize_pending_action(row) for row in rows]}

    def approve_action(self, action_id: int) -> dict:
        return serialize_pending_action(self.gate.approve(action_id))

    def reject_action(self, action_id: int) -> dict:
        return serialize_pending_action(self.gate.reject(action_id))

    def mark_user_completed(self, action_id: int) -> dict:
        action = self.gate.mark_user_completed(action_id)
        if action.portal_session_id:
            session = self._get_session(action.portal_session_id)
            if session.status in {"waiting_user_login", "waiting_user_captcha"}:
                session.status = "logged_in"
                self.db.commit()
        return serialize_pending_action(action)

    def _execute_with_executor(self, session: PortalSession, action: PendingAction) -> dict[str, Any]:
        executor = self._get_executor(session.executor_type)
        browser_session = settings.opencli_session
        target = action.target_selector or action.target_label or action.action_type
        value = action.proposed_value or ""
        if action.action_type == "fill_field":
            return executor.fill(browser_session, target, value)
        if action.action_type == "upload_document":
            return {
                "status": "success",
                "message": "Prepared local document path for portal upload.",
                "session": browser_session,
                "target": target,
                "file_path": value,
                "value_preview": _preview(value),
            }
        if action.action_type == "save_draft":
            return executor.click(browser_session, target)
        if action.action_type == "navigate_next":
            return executor.click(browser_session, target)
        return executor.click(browser_session, target)

    def execute_action(self, action_id: int) -> dict:
        action = self.gate.get_action(action_id)
        self.gate.assert_executable(action)
        session = self._get_session(action.portal_session_id) if action.portal_session_id else None
        if not session:
            raise HTTPException(status_code=404, detail="Portal session not found")
        result = self._execute_with_executor(session, action)
        if result.get("status") == "blocked":
            raise HTTPException(status_code=400, detail=result.get("message") or "Executor blocked this action")
        if result.get("status") != "success":
            self.audit.create(
                applicant_id=action.applicant_id,
                action=f"execute_failed:{action.action_type}",
                actor="browser_agent",
                risk={"risk_level": action.risk_level, "requires_approval": action.requires_approval, "blocked": action.blocked},
                message=result.get("message") or "Executor could not complete this action.",
                metadata={
                    "pending_action_id": action.id,
                    "portal_session_id": action.portal_session_id,
                    "target": action.target_label,
                    "executor_type": session.executor_type,
                    "executor_status": result.get("status"),
                },
                commit=True,
            )
            raise HTTPException(status_code=503, detail=result.get("message") or "Browser executor unavailable")
        was_approved = action.status == "approved"
        action.status = "executed"
        if action.action_type == "save_draft":
            session.status = "saved_draft"
        else:
            session.status = "filling"
        self.audit.create(
            applicant_id=action.applicant_id,
            action=f"execute:{action.action_type}",
            actor="browser_agent",
            risk={"risk_level": action.risk_level, "requires_approval": action.requires_approval, "blocked": action.blocked},
            approved_by_user=was_approved,
            message=result.get("message") or "Executed pending browser action.",
            metadata={
                "pending_action_id": action.id,
                "portal_session_id": action.portal_session_id,
                "target": action.target_label,
                "value_preview": _preview(action.proposed_value),
                "executor_type": session.executor_type,
                "executor_status": result.get("status"),
            },
            commit=False,
        )
        self.db.commit()
        self.db.refresh(action)
        return {"action": serialize_pending_action(action), "result": result, "session": serialize_session(session)}

    def run_fill_step(self, session_id: int) -> dict:
        action = (
            self.db.query(PendingAction)
            .filter(
                PendingAction.portal_session_id == session_id,
                PendingAction.status == "pending",
                PendingAction.blocked.is_(False),
            )
            .order_by(PendingAction.requires_approval.asc(), PendingAction.id.asc())
            .first()
        )
        if not action:
            return {"session_id": session_id, "message": "No executable pending actions."}
        return self.execute_action(action.id)

    def stop(self, session_id: int) -> dict:
        session = self._get_session(session_id)
        session.status = "stopped_before_submit"
        self.audit.create(
            applicant_id=session.applicant_id,
            action="portal_session:stop",
            actor="user",
            risk={"risk_level": "low", "requires_approval": False, "blocked": False},
            approved_by_user=True,
            message="Portal assistant stopped by user.",
            metadata={"portal_session_id": session.id},
            commit=False,
        )
        self.db.commit()
        self.db.refresh(session)
        return serialize_session(session)

    def get_logs(self, session_id: int) -> dict:
        session = self._get_session(session_id)
        pattern = f'%"portal_session_id": {session_id}%'
        rows = (
            self.db.query(AuditLog)
            .filter(AuditLog.applicant_id == session.applicant_id, AuditLog.metadata_json.like(pattern))
            .order_by(AuditLog.id.asc())
            .all()
        )
        return {"session_id": session_id, "logs": [serialize_audit_log(row) for row in rows]}
