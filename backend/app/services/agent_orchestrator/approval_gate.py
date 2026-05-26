from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import PendingAction
from app.services.agent_orchestrator.audit_log_service import AuditLogService
from app.services.browser_agent.risk_guard import RiskGuard


def serialize_pending_action(action: PendingAction) -> dict:
    return {column.name: getattr(action, column.name) for column in action.__table__.columns}


class ApprovalGate:
    def __init__(self, db: Session):
        self.db = db
        self.risk_guard = RiskGuard()
        self.audit = AuditLogService(db)

    def propose(
        self,
        *,
        applicant_id: int,
        program_id: int | None,
        portal_session_id: int | None,
        action_type: str,
        target_label: str | None = None,
        target_selector: str | None = None,
        proposed_value: str | None = None,
        description: str | None = None,
        agent_task_id: int | None = None,
        force_blocked_reason: str | None = None,
    ) -> PendingAction:
        risk = self.risk_guard.classify(" ".join(filter(None, [action_type, target_label, description])))
        if force_blocked_reason:
            risk = {
                "risk_level": "high",
                "requires_approval": True,
                "blocked": True,
                "reason": force_blocked_reason,
            }
        action = PendingAction(
            applicant_id=applicant_id,
            program_id=program_id,
            portal_session_id=portal_session_id,
            agent_task_id=agent_task_id,
            action_type=action_type,
            target_label=target_label,
            target_selector=target_selector,
            proposed_value=proposed_value[:5000] if proposed_value else None,
            description=description,
            risk_level=risk["risk_level"],
            requires_approval=risk["requires_approval"],
            blocked=risk["blocked"],
            status="blocked" if risk["blocked"] else "pending",
            reason=risk["reason"],
        )
        self.db.add(action)
        self.db.flush()
        self.audit.create(
            applicant_id=applicant_id,
            agent_task_id=agent_task_id,
            action=f"propose:{action_type}",
            actor="ai",
            risk=risk,
            message=f"Proposed browser action: {description or target_label or action_type}",
            metadata={"pending_action_id": action.id, "portal_session_id": portal_session_id},
            commit=False,
        )
        return action

    def get_action(self, action_id: int) -> PendingAction:
        action = self.db.get(PendingAction, action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Pending action not found")
        return action

    def approve(self, action_id: int) -> PendingAction:
        action = self.get_action(action_id)
        if action.blocked:
            raise HTTPException(status_code=400, detail="Blocked actions cannot be approved for automation")
        if action.status == "rejected":
            raise HTTPException(status_code=400, detail="Rejected actions cannot be approved")
        action.status = "approved"
        self.audit.create(
            applicant_id=action.applicant_id,
            agent_task_id=action.agent_task_id,
            action=f"approve:{action.action_type}",
            actor="user",
            risk={"risk_level": action.risk_level, "requires_approval": action.requires_approval, "blocked": action.blocked},
            approved_by_user=True,
            message="User approved pending browser action.",
            metadata={"pending_action_id": action.id, "portal_session_id": action.portal_session_id},
            commit=False,
        )
        self.db.commit()
        self.db.refresh(action)
        return action

    def reject(self, action_id: int) -> PendingAction:
        action = self.get_action(action_id)
        action.status = "rejected"
        self.audit.create(
            applicant_id=action.applicant_id,
            agent_task_id=action.agent_task_id,
            action=f"reject:{action.action_type}",
            actor="user",
            risk={"risk_level": action.risk_level, "requires_approval": action.requires_approval, "blocked": action.blocked},
            message="User rejected pending browser action.",
            metadata={"pending_action_id": action.id, "portal_session_id": action.portal_session_id},
            commit=False,
        )
        self.db.commit()
        self.db.refresh(action)
        return action

    def mark_user_completed(self, action_id: int) -> PendingAction:
        action = self.get_action(action_id)
        action.status = "user_completed"
        self.audit.create(
            applicant_id=action.applicant_id,
            agent_task_id=action.agent_task_id,
            action=f"user_completed:{action.action_type}",
            actor="user",
            risk={"risk_level": action.risk_level, "requires_approval": action.requires_approval, "blocked": action.blocked},
            approved_by_user=True,
            message="User completed this step manually on the official portal.",
            metadata={"pending_action_id": action.id, "portal_session_id": action.portal_session_id},
            commit=False,
        )
        self.db.commit()
        self.db.refresh(action)
        return action

    def assert_executable(self, action: PendingAction) -> None:
        if action.blocked:
            raise HTTPException(status_code=400, detail="Blocked actions cannot be executed by ApplyPilot")
        if action.status == "rejected":
            raise HTTPException(status_code=400, detail="Rejected actions cannot be executed")
        if action.risk_level == "medium" and action.status != "approved":
            raise HTTPException(status_code=400, detail="Medium-risk actions require approval before execution")
        if action.status not in {"pending", "approved"}:
            raise HTTPException(status_code=400, detail=f"Action with status {action.status} cannot be executed")
