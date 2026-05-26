from pydantic import BaseModel


class BrowserTaskRequest(BaseModel):
    applicant_id: int | None = 1
    program_id: int | None = None
    task_name: str = "Fill local sample application form"
