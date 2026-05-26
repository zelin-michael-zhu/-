import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Application, Program, ProgramDocument
from app.services.documents.document_service import DocumentService

router = APIRouter(prefix="/applications", tags=["applications"])

VALID_STATUSES = {"Not Started", "In Progress", "Submitted", "Interview", "Offer", "Rejected"}


def _program_document_names(db: Session, program: Program) -> list[str]:
    docs = db.query(ProgramDocument).filter(ProgramDocument.program_id == program.id, ProgramDocument.required.is_(True)).all()
    if docs:
        return [doc.document_type for doc in docs]
    fallback: list[str] = []
    if program.cv_required:
        fallback.append("CV")
    if program.personal_statement_required:
        fallback.append("Personal Statement")
    if program.transcript_required:
        fallback.append("Transcript")
    if program.recommendation_letters_required:
        for idx in range(program.recommendation_letters_required):
            fallback.append(f"Recommendation Letter {idx + 1}")
    if program.ielts_requirement or program.toefl_requirement or program.language_requirement:
        fallback.append("Language Test Score")
    return fallback or ["CV", "Personal Statement", "Transcript"]


def serialize_application(item: Application) -> dict:
    data = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    if item.program:
        data["program"] = {
            "id": item.program.id,
            "program_name": item.program.program_name,
            "university_name": item.program.university.name if item.program.university else None,
            "country": item.program.country,
            "field": item.program.field,
            "application_deadline": item.program.application_deadline,
        }
    else:
        data["program"] = None
    try:
        data["missing_items"] = json.loads(item.missing_items_json or "[]")
    except Exception:
        data["missing_items"] = []
    return data


@router.get("")
def list_applications(applicant_id: int | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Application)
    if applicant_id is not None:
        query = query.filter(Application.applicant_id == applicant_id)
    items = query.order_by(Application.id).all()
    return [serialize_application(item) for item in items]


@router.post("")
def create_application(payload: dict, db: Session = Depends(get_db)):
    applicant_id = payload.get("applicant_id")
    program_id = payload.get("program_id")
    if not applicant_id or not program_id:
        raise HTTPException(status_code=400, detail="applicant_id and program_id are required")
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    existing = db.query(Application).filter(Application.applicant_id == applicant_id, Application.program_id == program_id).first()
    if existing:
        return serialize_application(existing)
    missing = DocumentService(db).missing_document_names_for_program(applicant_id, program_id)
    item = Application(
        applicant_id=applicant_id,
        program_id=program_id,
        status="Not Started",
        deadline=payload.get("deadline") or program.application_deadline,
        missing_items_json=json.dumps(missing, ensure_ascii=False),
        notes=payload.get("notes"),
        last_activity=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_application(item)


@router.put("/{application_id}")
def update_application(application_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Application, application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in payload.items():
        if key in {"status", "deadline", "missing_items_json", "notes"} and hasattr(item, key):
            setattr(item, key, value)
    item.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return serialize_application(item)


@router.put("/{application_id}/status")
def update_status(application_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Application, application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    status = payload.get("status", item.status)
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid application status")
    item.status = status
    item.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return serialize_application(item)


@router.post("/{application_id}/refresh-missing-items")
def refresh_missing_items(application_id: int, db: Session = Depends(get_db)):
    item = db.get(Application, application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    missing = DocumentService(db).missing_document_names_for_program(item.applicant_id, item.program_id)
    item.missing_items_json = json.dumps(missing, ensure_ascii=False)
    item.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return serialize_application(item)
