from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UniversityCreate(BaseModel):
    name: str
    short_name: str | None = None
    country: str
    city: str | None = None
    official_website: str | None = None
    admissions_website: str | None = None
    ranking_note: str | None = None


class UniversityOut(UniversityCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
