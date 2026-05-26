import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Applicant, BrowserTask, Program
from app.services.browser_agent.mock_executor import MockExecutor
from app.services.browser_agent.opencli_executor import OpenCLIExecutor
from app.services.browser_agent.opencli_health import check_opencli_health
from app.services.browser_agent.playwright_executor import PlaywrightExecutor
from app.services.browser_agent.risk_guard import RiskGuard
from app.services.documents.document_service import DocumentService


def _now() -> str:
    return datetime.utcnow().isoformat()


def _preview(value: str | None) -> str | None:
    if value is None:
        return None
    return value[:20]


def _loads(raw: str | None) -> list[dict]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _dumps(logs: list[dict]) -> str:
    return json.dumps(logs, ensure_ascii=False)


def make_log(
    executor: str,
    action: str,
    target: str | None = None,
    value: str | None = None,
    status: str = "success",
    message: str = "",
    risk: dict | None = None,
) -> dict:
    risk = risk or RiskGuard().classify(f"{action} {target or ''}")
    return {
        "time": _now(),
        "executor": executor,
        "action": action,
        "target": target,
        "value_preview": _preview(value),
        "risk_level": risk["risk_level"],
        "requires_approval": risk["requires_approval"],
        "blocked": risk["blocked"],
        "status": status,
        "message": message or risk["reason"],
    }


class BrowserAgentService:
    def __init__(self, db: Session):
        self.db = db

    def get_executor(self, executor_type: str):
        if executor_type == "playwright":
            return PlaywrightExecutor()
        if executor_type == "opencli":
            return OpenCLIExecutor()
        return MockExecutor()

    def list_executors(self) -> dict:
        executors = [MockExecutor(), PlaywrightExecutor(), OpenCLIExecutor()]
        return {"executors": [executor.check_available() for executor in executors]}

    def _task_context(self, applicant_id: int | None, program_id: int | None) -> dict:
        try:
            applicant = self.db.get(Applicant, applicant_id) if applicant_id else None
        except Exception:
            applicant = None
        try:
            program = self.db.get(Program, program_id) if program_id else None
        except Exception:
            program = None
        documents = None
        if applicant_id and program_id:
            try:
                documents = DocumentService(self.db).get_document_availability_for_program(applicant_id, program_id)
            except Exception as exc:
                documents = {"warnings": [f"Document availability could not be computed: {exc}"], "available_documents": {}, "missing_documents": []}
        return {
            "applicant": {
                "id": applicant.id,
                "full_name": applicant.full_name,
                "email": applicant.email,
                "university": applicant.university,
                "major": applicant.major,
                "gpa": applicant.gpa_converted_4 or applicant.gpa_value,
            } if applicant else None,
            "program": {
                "id": program.id,
                "program_name": program.program_name,
                "university_name": program.university.name if program.university else None,
            } if program else None,
            "documents": documents,
        }

    def start_task(self, applicant_id: int | None, program_id: int | None, executor_type: str | None = None) -> BrowserTask:
        executor_type = executor_type or settings.browser_executor_default
        executor = self.get_executor(executor_type)
        available = executor.check_available()
        status = "running" if available.get("available") else "failed"
        context = self._task_context(applicant_id, program_id)
        logs = [
            make_log(
                executor_type,
                "start_task",
                status=status,
                message=available.get("message", f"{executor_type} executor selected."),
            )
        ]
        logs.append(
            {
                "time": _now(),
                "executor": executor_type,
                "action": "load_context",
                "target": "applicant_program",
                "value_preview": None,
                "risk_level": "low",
                "requires_approval": False,
                "blocked": False,
                "status": "success",
                "message": "Loaded applicant and program context for form prefilling.",
                "context": context,
            }
        )
        task = BrowserTask(
            applicant_id=applicant_id,
            program_id=program_id,
            task_name=f"Fill local sample application form ({executor_type})",
            status=status,
            current_step="Task initialized" if status == "running" else "Executor unavailable",
            logs_json=_dumps(logs),
            requires_approval=False,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def _get_task(self, task_id: int) -> BrowserTask:
        task = self.db.get(BrowserTask, task_id)
        if not task:
            raise ValueError(f"Browser task {task_id} not found")
        return task

    def _executor_type_for(self, task: BrowserTask) -> str:
        logs = _loads(task.logs_json)
        if logs and logs[0].get("executor"):
            return str(logs[0]["executor"])
        if "(" in task.task_name and ")" in task.task_name:
            return task.task_name.rsplit("(", 1)[-1].rstrip(")")
        return settings.browser_executor_default

    def run_next_step(self, task_id: int) -> dict:
        task = self._get_task(task_id)
        executor_type = self._executor_type_for(task)
        executor = self.get_executor(executor_type)
        logs = _loads(task.logs_json)
        if task.status in {"stopped", "completed", "failed"}:
            return {"task_id": task.id, "status": task.status, "logs": logs}
        if executor_type == "playwright":
            context = self._task_context(task.applicant_id, task.program_id)
            applicant_context = context.get("applicant") or {}
            result = executor.run_local_form_demo({
                "full_name": applicant_context.get("full_name"),
                "email": applicant_context.get("email"),
                "university": applicant_context.get("university"),
                "major": applicant_context.get("major"),
                "gpa": applicant_context.get("gpa"),
            })
            risk = result.get("risk") or RiskGuard().classify("save draft")
            log = make_log(executor_type, "save_draft", "sample_application_form", status=result["status"], message=result.get("message", ""), risk=risk)
            task.status = "completed" if result["status"] == "success" else "failed"
            task.current_step = "Local form demo completed"
        elif executor_type == "opencli":
            result = executor.get_state(settings.opencli_session)
            risk = result.get("risk") or RiskGuard().classify("get state")
            log = make_log(executor_type, "get_state", settings.opencli_session, status=result["status"], message=result.get("message", "Read OpenCLI browser state."), risk=risk)
            task.status = "waiting_approval" if risk["requires_approval"] else ("running" if result["status"] in {"success", "unavailable"} else "failed")
            task.current_step = "OpenCLI state check"
        else:
            context = self._task_context(task.applicant_id, task.program_id)
            full_name = ((context.get("applicant") or {}).get("full_name") or "").strip()
            first_name = full_name.split(" ", 1)[0] if full_name else "Applicant"
            result = executor.fill(settings.opencli_session, "first_name", first_name)
            risk = RiskGuard().classify("fill first_name")
            log = make_log(executor_type, "fill", "first_name", first_name, result["status"], result.get("message", ""), risk)
            task.status = "waiting_approval"
            task.current_step = "Review next mock action"
            task.requires_approval = True
        logs.append(log)
        task.logs_json = _dumps(logs)
        self.db.commit()
        self.db.refresh(task)
        return {"task_id": task.id, "status": task.status, "result": result, "logs": logs}

    def approve_action(self, task_id: int, action_id: str) -> dict:
        task = self._get_task(task_id)
        executor_type = self._executor_type_for(task)
        risk = RiskGuard().classify(f"approve {action_id}")
        logs = _loads(task.logs_json)
        logs.append(make_log(executor_type, "approve", action_id, status="success", message="Human approved action.", risk=risk))
        task.status = "running"
        task.requires_approval = False
        task.current_step = "Action approved"
        task.logs_json = _dumps(logs)
        self.db.commit()
        self.db.refresh(task)
        return {"task_id": task.id, "status": task.status, "logs": logs}

    def stop_task(self, task_id: int) -> dict:
        task = self._get_task(task_id)
        executor_type = self._executor_type_for(task)
        logs = _loads(task.logs_json)
        logs.append(make_log(executor_type, "stop", status="success", message="Browser task stopped by user."))
        task.status = "stopped"
        task.current_step = "Stopped by user"
        task.logs_json = _dumps(logs)
        self.db.commit()
        self.db.refresh(task)
        return {"task_id": task.id, "status": task.status, "logs": logs}

    def get_logs(self, task_id: int) -> dict:
        task = self._get_task(task_id)
        return {"task_id": task.id, "status": task.status, "logs": _loads(task.logs_json)}


def build_mock_logs() -> list[str]:
    return [
        "High-risk actions require human approval.",
        "Passwords, payment, CAPTCHA bypass, and final submit are disabled.",
        "All browser actions are logged for review.",
    ]


def get_opencli_status() -> dict:
    return check_opencli_health()
