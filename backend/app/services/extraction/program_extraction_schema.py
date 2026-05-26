from pydantic import BaseModel


class ProgramExtraction(BaseModel):
    program_name: str | None = None
    degree_type: str | None = None
    field: str | None = None
    faculty: str | None = None
    department: str | None = None
    duration: str | None = None
    study_mode: str | None = None
    tuition_amount: float | None = None
    tuition_currency: str | None = None
    tuition_note: str | None = None
    application_deadline: str | None = None
    deadline_note: str | None = None
    intake: str | None = None
    application_url: str | None = None
    program_url: str | None = None
    requirements_url: str | None = None
    curriculum_url: str | None = None
    description: str | None = None
    curriculum_summary: str | None = None
    career_summary: str | None = None
    language_requirement: str | None = None
    ielts_requirement: str | None = None
    toefl_requirement: str | None = None
    gre_required: bool | None = None
    gmat_required: bool | None = None
    gpa_requirement: str | None = None
    work_experience_required: str | None = None
    recommendation_letters_required: int | None = None
    personal_statement_required: bool | None = None
    cv_required: bool | None = None
    transcript_required: bool | None = None
    application_fee: float | None = None
    application_fee_currency: str | None = None
    scholarship_info: str | None = None
    required_documents: list[str] = []
    deadlines: list[dict] = []
    requirements: list[dict] = []
    confidence: float = 0.5
    missing_fields: list[str] = []
    source_evidence: list[dict] = []
