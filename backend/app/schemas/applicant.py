from pydantic import BaseModel, ConfigDict


class ApplicantUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    university: str | None = None
    college: str | None = None
    major: str | None = None
    degree: str | None = None
    graduation_year: int | None = None
    gpa_value: float | None = None
    gpa_scale: float | None = None
    ranking: str | None = None
    ielts: float | None = None
    toefl: int | None = None
    gre: int | None = None
    gmat: int | None = None
    target_countries_json: str | None = None
    target_fields_json: str | None = None
    preference_priority: str | None = None
    budget: float | None = None
    experiences_json: str | None = None
    awards_json: str | None = None
    papers_json: str | None = None


class ApplicantOut(ApplicantUpdate):
    id: int
    gpa_converted_4: float | None = None
    target_countries_json: str | None = None
    target_fields_json: str | None = None
    model_config = ConfigDict(from_attributes=True)
