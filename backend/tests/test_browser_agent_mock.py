from app.models import BrowserTask
from app.services.browser_agent.browser_agent_service import BrowserAgentService
from app.services.browser_agent.mock_executor import MockExecutor


class FakeDb:
    def __init__(self):
        self.items = {}
        self.next_id = 1

    def add(self, item):
        item.id = self.next_id
        self.next_id += 1
        self.items[item.id] = item

    def commit(self):
        return None

    def refresh(self, item):
        return item

    def get(self, model, item_id):
        assert model is BrowserTask
        return self.items.get(item_id)


def test_mock_executor_available():
    assert MockExecutor().check_available()["available"] is True


def test_start_task_and_run_next_step_with_mock():
    service = BrowserAgentService(FakeDb())
    task = service.start_task(applicant_id=1, program_id=1, executor_type="mock")
    assert task.status == "running"
    result = service.run_next_step(task.id)
    assert result["status"] == "waiting_approval"
    assert result["logs"]
