import shutil
import subprocess

from app.services.browser_agent.browser_executor_base import BrowserExecutorBase
from app.services.browser_agent.opencli_command_builder import (
    build_click_command,
    build_close_command,
    build_extract_command,
    build_fill_command,
    build_open_command,
    build_screenshot_command,
    build_select_command,
    build_state_command,
    build_type_command,
    build_wait_command,
)
from app.services.browser_agent.opencli_health import check_opencli_health
from app.services.browser_agent.risk_guard import RiskGuard


class OpenCLIExecutor(BrowserExecutorBase):
    executor_type = "opencli"

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.risk_guard = RiskGuard()

    def check_available(self) -> dict:
        health = check_opencli_health()
        return {"type": self.executor_type, "available": health["installed"] and health["doctor_ok"], **health}

    def _run(self, command: list[str], action_text: str) -> dict:
        risk = self.risk_guard.classify(action_text)
        if risk["blocked"]:
            return {"status": "blocked", "command": command, "risk": risk}
        if not shutil.which("opencli"):
            return {
                "status": "unavailable",
                "command": command,
                "risk": risk,
                "message": "OpenCLI is not installed. Please run npm install -g @jackwener/opencli and opencli doctor.",
            }
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
            shell=False,
        )
        return {
            "status": "success" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "command": command,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "risk": risk,
        }

    def open_url(self, session: str, url: str) -> dict:
        return self._run(build_open_command(session, url), f"open {url}")

    def get_state(self, session: str) -> dict:
        return self._run(build_state_command(session), "get browser state")

    def click(self, session: str, target: str) -> dict:
        return self._run(build_click_command(session, target), f"click {target}")

    def fill(self, session: str, field: str, value: str) -> dict:
        return self._run(build_fill_command(session, field, value), f"fill {field}")

    def type_text(self, session: str, text: str) -> dict:
        return self._run(build_type_command(session, text), f"type {text[:20]}")

    def select(self, session: str, field: str, value: str) -> dict:
        return self._run(build_select_command(session, field, value), f"select {field}")

    def extract(self, session: str, instruction: str) -> dict:
        return self._run(build_extract_command(session, instruction), f"extract {instruction}")

    def screenshot(self, session: str) -> dict:
        return self._run(build_screenshot_command(session), "screenshot")

    def wait(self, session: str, condition: str) -> dict:
        return self._run(build_wait_command(session, condition), f"wait {condition}")

    def close(self, session: str) -> dict:
        return self._run(build_close_command(session), "close browser session")
