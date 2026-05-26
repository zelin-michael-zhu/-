import asyncio
from pathlib import Path

from app.services.browser_agent.browser_executor_base import BrowserExecutorBase
from app.services.browser_agent.risk_guard import RiskGuard


class PlaywrightExecutor(BrowserExecutorBase):
    executor_type = "playwright"

    def __init__(self):
        self.risk_guard = RiskGuard()

    def check_available(self) -> dict:
        try:
            import playwright  # noqa: F401
            return {"type": self.executor_type, "available": True, "message": "Playwright package is installed."}
        except Exception as exc:
            return {"type": self.executor_type, "available": False, "message": str(exc)}

    async def _run_local_form_demo(self, applicant: dict | None = None) -> dict:
        from playwright.async_api import async_playwright

        applicant = applicant or {}
        full_name = str(applicant.get("full_name") or "Zeklin Zhu").strip()
        parts = full_name.split(" ", 1)
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""
        root = Path(__file__).resolve().parents[2]
        form = root / "demo_pages" / "sample_application_form.html"
        screenshots = root.parent / "screenshots"
        screenshots.mkdir(exist_ok=True)
        screenshot_path = screenshots / "sample_application_form.png"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            await page.goto(form.as_uri())
            await page.fill('input[name="first_name"]', first_name)
            await page.fill('input[name="last_name"]', last_name)
            await page.fill('input[name="email"]', str(applicant.get("email") or "demo@applypilot.local"))
            await page.fill('input[name="nationality"]', str(applicant.get("nationality") or "China"))
            await page.fill('input[name="university"]', str(applicant.get("university") or "BNU-HKBU United International College"))
            await page.fill('input[name="major"]', str(applicant.get("major") or "Business Analytics"))
            await page.fill('input[name="gpa"]', str(applicant.get("gpa") or "3.62/4.0"))
            await page.click("#save")
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await browser.close()
        return {
            "status": "success",
            "message": "Filled local sample form and clicked Save Draft. Submit was not clicked.",
            "screenshot_path": str(screenshot_path),
        }

    def run_local_form_demo(self, applicant: dict | None = None) -> dict:
        risk = self.risk_guard.classify("save draft local sample form")
        if risk["blocked"]:
            return {"status": "blocked", "risk": risk}
        result = asyncio.run(self._run_local_form_demo(applicant))
        result["risk"] = risk
        return result

    def open_url(self, session: str, url: str) -> dict:
        if not url.startswith("file://"):
            return {"status": "blocked", "message": "Playwright MVP only opens the local sample application form."}
        return {"status": "success", "session": session, "url": url}

    def get_state(self, session: str) -> dict:
        return {"status": "success", "session": session, "state": {"mode": "local-demo"}}

    def click(self, session: str, target: str) -> dict:
        risk = self.risk_guard.classify(f"click {target}")
        return {"status": "blocked" if risk["blocked"] else "success", "session": session, "target": target, "risk": risk}

    def fill(self, session: str, field: str, value: str) -> dict:
        risk = self.risk_guard.classify(f"fill {field}")
        return {"status": "blocked" if risk["blocked"] else "success", "session": session, "field": field, "value_preview": value[:20], "risk": risk}

    def type_text(self, session: str, text: str) -> dict:
        return {"status": "success", "session": session, "value_preview": text[:20]}

    def select(self, session: str, field: str, value: str) -> dict:
        return {"status": "success", "session": session, "field": field, "value": value}

    def extract(self, session: str, instruction: str) -> dict:
        return {"status": "success", "session": session, "instruction": instruction}

    def screenshot(self, session: str) -> dict:
        return {"status": "success", "session": session}

    def wait(self, session: str, condition: str) -> dict:
        return {"status": "success", "session": session, "condition": condition}

    def close(self, session: str) -> dict:
        return {"status": "success", "session": session}
