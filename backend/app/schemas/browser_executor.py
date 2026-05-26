from pydantic import BaseModel


class StartBrowserTaskRequest(BaseModel):
    applicant_id: int | None = 1
    program_id: int | None = None
    executor_type: str = "mock"


class TaskIdRequest(BaseModel):
    task_id: int


class ApproveActionRequest(BaseModel):
    task_id: int
    action_id: str = "next"
