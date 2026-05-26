import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import ExtractionRun, Program, ProgramDeadline, ProgramDocument, ProgramRequirement, RawPage
from app.services.extraction.mock_llm_extractor import extract_program


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    text = raw.strip().rstrip(".")
    try:
        return date.fromisoformat(text[:10])
    except Exception:
        return None


def _upsert_program(db: Session, page: RawPage, result) -> Program:
    status = "auto_extracted" if result.confidence >= 0.75 else "needs_review"
    existing = db.query(Program).filter(Program.source_url == page.url).first()
    program = existing or Program(source_url=page.url)
    program.university_id = page.university_id
    program.program_name = result.program_name or page.title or "Auto-extracted Master Program"
    program.normalized_program_name = program.program_name.lower()
    program.degree_type = result.degree_type
    program.field = result.field
    program.faculty = result.faculty
    program.department = result.department
    program.duration = result.duration
    program.study_mode = result.study_mode
    program.tuition_amount = result.tuition_amount
    program.tuition_currency = result.tuition_currency
    program.tuition_note = result.tuition_note
    program.application_deadline = _parse_date(result.application_deadline)
    program.deadline_note = result.deadline_note
    program.intake = result.intake
    program.application_url = result.application_url
    program.program_url = result.program_url or page.url
    program.requirements_url = result.requirements_url
    program.curriculum_url = result.curriculum_url
    program.description = result.description or (page.text_content or "")[:800]
    program.curriculum_summary = result.curriculum_summary
    program.career_summary = result.career_summary
    program.language_requirement = result.language_requirement
    program.ielts_requirement = result.ielts_requirement
    program.toefl_requirement = result.toefl_requirement
    program.gre_required = result.gre_required
    program.gmat_required = result.gmat_required
    program.gpa_requirement = result.gpa_requirement
    program.work_experience_required = bool(result.work_experience_required)
    program.recommendation_letters_required = result.recommendation_letters_required
    program.personal_statement_required = result.personal_statement_required
    program.cv_required = result.cv_required
    program.transcript_required = result.transcript_required
    program.application_fee = result.application_fee
    program.application_fee_currency = result.application_fee_currency
    program.scholarship_info = result.scholarship_info
    program.raw_text_snapshot = (page.text_content or "")[:20000]
    program.extraction_confidence = result.confidence
    program.review_status = status
    program.last_checked = datetime.utcnow()
    if not existing:
        db.add(program)
        db.flush()
    db.query(ProgramDocument).filter(ProgramDocument.program_id == program.id).delete()
    db.query(ProgramDeadline).filter(ProgramDeadline.program_id == program.id).delete()
    db.query(ProgramRequirement).filter(ProgramRequirement.program_id == program.id).delete()
    for doc in result.required_documents:
        db.add(ProgramDocument(program_id=program.id, document_type=doc, required=True, quantity=1, description=doc, source_url=page.url))
    for deadline in result.deadlines:
        db.add(ProgramDeadline(program_id=program.id, round_name=deadline.get("round_name"), deadline_date=_parse_date(deadline.get("deadline_date")), deadline_text=deadline.get("deadline_text"), intake=deadline.get("intake"), is_international=deadline.get("is_international"), source_url=deadline.get("source_url") or page.url))
    for req in [item for item in result.requirements if item]:
        db.add(ProgramRequirement(program_id=program.id, requirement_type=req.get("requirement_type", "general"), requirement_name=req.get("requirement_name", "Requirement"), requirement_value=req.get("requirement_value"), required=req.get("required", True), notes=req.get("notes"), source_url=req.get("source_url") or page.url))
    return program


def extract_raw_pages(db: Session, limit: int = 20, university_id: int | None = None, raw_page_id: int | None = None, provider: str = "mock") -> dict:
    query = db.query(RawPage)
    if raw_page_id:
        query = query.filter(RawPage.id == raw_page_id)
    if university_id:
        query = query.filter(RawPage.university_id == university_id)
    pages = query.order_by(RawPage.id.desc()).limit(limit).all()
    count = 0
    program_ids: list[int] = []
    for page in pages:
        try:
            result = extract_program(page.text_content or "", page.url)
            program = _upsert_program(db, page, result)
            db.add(ExtractionRun(raw_page_id=page.id, model_name=provider, extracted_json=result.model_dump_json(), confidence=result.confidence, status="success"))
            program_ids.append(program.id)
            count += 1
        except Exception as exc:
            db.add(ExtractionRun(raw_page_id=page.id, model_name=provider, extracted_json=json.dumps({}), confidence=0, status="failed", error_message=str(exc)))
    db.commit()
    return {"extracted_programs": count, "program_ids": program_ids, "provider": provider}
