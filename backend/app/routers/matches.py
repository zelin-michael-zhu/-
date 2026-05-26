import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Applicant, Program, ProgramMatch
from app.services.matching.matching_service import category, score_program

router = APIRouter(prefix="/matches", tags=["matches"])


def serialize_match(row: ProgramMatch) -> dict:
    program = row.program
    return {
        "id": row.id,
        "applicant_id": row.applicant_id,
        "program_id": row.program_id,
        "match_score": row.match_score,
        "score": row.match_score,
        "category": row.category,
        "reasons": json.loads(row.reasons_json or "[]"),
        "risks": json.loads(row.risks_json or "[]"),
        "program": {
            "id": program.id,
            "program_name": program.program_name,
            "university_name": program.university.name if program.university else None,
            "country": program.country,
            "field": program.field,
            "degree_type": program.degree_type,
            "application_deadline": program.application_deadline,
            "tuition_amount": program.tuition_amount,
            "tuition_currency": program.tuition_currency,
            "extraction_confidence": program.extraction_confidence,
            "review_status": program.review_status,
        },
    }


@router.post("/generate/{applicant_id}")
def generate_matches(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    db.query(ProgramMatch).filter(ProgramMatch.applicant_id == applicant_id).delete()
    programs = db.query(Program).filter(
        (Program.review_status == "reviewed") |
        ((Program.review_status == "auto_extracted") & (Program.extraction_confidence >= 0.85))
    ).all()
    if not programs:
        programs = db.query(Program).all()
    for program in programs:
        score, reasons, risks = score_program(applicant, program)
        db.add(ProgramMatch(applicant_id=applicant_id, program_id=program.id, match_score=score, category=category(score), reasons_json=json.dumps(reasons), risks_json=json.dumps(risks)))
    db.commit()
    rows = db.query(ProgramMatch).filter(ProgramMatch.applicant_id == applicant_id).order_by(ProgramMatch.match_score.desc()).all()
    return {"status": "generated", "total": len(rows), "items": [serialize_match(row) for row in rows]}


@router.get("/{applicant_id}")
def list_matches(applicant_id: int, db: Session = Depends(get_db)):
    rows = db.query(ProgramMatch).filter(ProgramMatch.applicant_id == applicant_id).order_by(ProgramMatch.match_score.desc()).all()
    return [serialize_match(row) for row in rows]
