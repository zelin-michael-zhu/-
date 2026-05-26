from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Applicant, Application, Document, Program, ProgramMatch
from app.routers.applicants import analyze_profile
from app.routers.applications import serialize_application
from app.routers.matches import serialize_match
from app.services.documents.document_service import DEFAULT_REQUIRED_DOCUMENTS, DocumentService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{applicant_id}")
def get_dashboard(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    analysis = analyze_profile(applicant)
    total_programs = db.query(Program).count()
    matches = (
        db.query(ProgramMatch)
        .filter(ProgramMatch.applicant_id == applicant_id)
        .order_by(ProgramMatch.match_score.desc())
        .all()
    )
    applications = (
        db.query(Application)
        .filter(Application.applicant_id == applicant_id)
        .order_by(Application.deadline.asc(), Application.id.asc())
        .all()
    )
    document_service = DocumentService(db)
    latest_documents = document_service.get_latest_documents_by_type(applicant_id)

    applications_by_status: dict[str, int] = {
        "Not Started": 0,
        "In Progress": 0,
        "Submitted": 0,
        "Interview": 0,
        "Offer": 0,
        "Rejected": 0,
    }
    for item in applications:
        applications_by_status[item.status] = applications_by_status.get(item.status, 0) + 1

    upcoming_deadlines = [
        serialize_application(item)
        for item in applications
        if item.deadline and item.deadline >= date.today()
    ][:6]
    missing_names: set[str] = set()
    if applications:
        for application in applications:
            for name in document_service.missing_document_names_for_program(applicant_id, application.program_id):
                missing_names.add(name)
    else:
        for name in DEFAULT_REQUIRED_DOCUMENTS[:3]:
            document = latest_documents.get(name.lower())
            if not document or document.status in {"missing", "draft", "deleted"}:
                missing_names.add(name)
    missing_documents = len(missing_names)

    tasks: list[dict] = []
    if analysis["completeness_percentage"] < 90:
        tasks.append({"title": "Complete profile details", "type": "profile", "priority": "high"})
    if not matches:
        tasks.append({"title": "Generate program matches", "type": "matches", "priority": "high"})
    if "CV" in missing_names:
        tasks.append({"title": "Upload CV", "title_zh": "上传 CV", "type": "documents", "priority": "high"})
    if "Transcript" in missing_names:
        tasks.append({"title": "Upload Transcript", "title_zh": "上传成绩单", "type": "documents", "priority": "high"})
    if "Personal Statement" in missing_names:
        tasks.append({"title": "Prepare Personal Statement", "title_zh": "准备个人陈述", "type": "documents", "priority": "medium"})
    ready_not_submitted = [doc for doc in latest_documents.values() if doc.status == "ready"]
    if ready_not_submitted:
        tasks.append({"title": "Submit prepared documents to application portal", "title_zh": "将已准备材料提交到申请系统", "type": "documents", "priority": "medium"})
    if upcoming_deadlines:
        tasks.append({"title": "Review upcoming application deadlines", "type": "applications", "priority": "medium"})

    return {
        "applicant": applicant,
        "profile_analysis": analysis,
        "stats": {
            "profile_strength": analysis["profile_strength_score"],
            "total_programs": total_programs,
            "matched_programs": len(matches),
            "applications": len(applications),
            "upcoming_deadlines": len(upcoming_deadlines),
            "missing_documents": missing_documents,
        },
        "top_matches": [serialize_match(item) for item in matches[:5]],
        "applications_by_status": applications_by_status,
        "upcoming_deadlines": upcoming_deadlines,
        "tasks": tasks,
    }
