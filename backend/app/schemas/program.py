from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class ProgramBase(BaseModel):
    university_id: int | None = None
    program_name: str
    degree_type: str | None = None
    field: str | None = None
    country: str | None = None
    city: str | None = None
    duration: str | None = None
    tuition_amount: float | None = None
    tuition_currency: str | None = None
    application_deadline: date | None = None
    source_url: str | None = None
    description: str | None = None
    ielts_requirement: str | None = None
    toefl_requirement: str | None = None
    gre_required: bool | None = None
    gmat_required: bool | None = None
    extraction_confidence: float | None = None
    review_status: str | None = "auto_extracted"


class ProgramCreate(ProgramBase):
    pass


class ProgramOut(ProgramBase):
    id: int
    university_name: str | None = None
    program_url: str | None = None
    raw_text_snapshot: str | None = None
    last_checked: datetime | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
