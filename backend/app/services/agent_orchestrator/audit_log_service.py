import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog


def _json(data: dict[str, Any] | None) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)


class AuditLogService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        applicant_id: int | None,
        action: str,
        actor: str = "system",
        risk: dict | None = None,
        application_plan_id: int | None = None,
        agent_task_id: int | None = None,
        approved_by_user: bool = False,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> AuditLog:
        risk = risk or {}
        log = AuditLog(
            applicant_id=applicant_id,
            application_plan_id=application_plan_id,
            agent_task_id=agent_task_id,
            actor=actor,
            action=action,
            risk_level=risk.get("risk_level"),
            requires_approval=bool(risk.get("requires_approval", False)),
            approved_by_user=approved_by_user,
            blocked=bool(risk.get("blocked", False)),
            message=message or risk.get("reason"),
            metadata_json=_json(metadata),
        )
        self.db.add(log)
        if commit:
            self.db.commit()
            self.db.refresh(log)
        return log
