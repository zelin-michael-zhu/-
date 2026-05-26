from app.services.browser_agent.browser_executor_base import BrowserExecutorBase


class MockExecutor(BrowserExecutorBase):
    executor_type = "mock"

    def check_available(self) -> dict:
        return {"type": self.executor_type, "available": True, "message": "Mock executor is always available."}

    def open_url(self, session: str, url: str) -> dict:
        return {"status": "success", "message": f"Mock opened {url}", "session": session}

    def get_state(self, session: str) -> dict:
        return {"status": "success", "session": session, "state": {"title": "Mock Application Form", "url": "mock://applypilot/form"}}

    def click(self, session: str, target: str) -> dict:
        return {"status": "success", "message": f"Mock clicked {target}", "session": session}

    def fill(self, session: str, field: str, value: str) -> dict:
        return {"status": "success", "message": f"Mock filled {field}", "session": session, "field": field, "value_preview": value[:20]}

    def type_text(self, session: str, text: str) -> dict:
        return {"status": "success", "message": "Mock typed text", "session": session, "value_preview": text[:20]}

    def select(self, session: str, field: str, value: str) -> dict:
        return {"status": "success", "message": f"Mock selected {value} for {field}", "session": session}

    def extract(self, session: str, instruction: str) -> dict:
        return {"status": "success", "message": "Mock extracted page information", "session": session, "instruction": instruction}

    def screenshot(self, session: str) -> dict:
        return {"status": "success", "message": "Mock screenshot captured", "session": session, "screenshot_path": None}

    def wait(self, session: str, condition: str) -> dict:
        return {"status": "success", "message": f"Mock waited for {condition}", "session": session}

    def close(self, session: str) -> dict:
        return {"status": "success", "message": "Mock session closed", "session": session}
