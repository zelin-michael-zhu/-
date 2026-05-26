from datetime import date
from pydantic import BaseModel, ConfigDict


class ApplicationIn(BaseModel):
    applicant_id: int
    program_id: int
    status: str = "Not Started"
    deadline: date | None = None
    notes: str | None = None


class ApplicationOut(ApplicationIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
