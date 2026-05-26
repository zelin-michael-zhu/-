from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Program, University

router = APIRouter(prefix="/programs", tags=["programs"])


def serialize_program(program: Program) -> dict:
    data = {c.name: getattr(program, c.name) for c in program.__table__.columns}
    data["university_name"] = program.university.name if program.university else None
    return data


@router.get("")
def list_programs(
    country: str | None = None,
    university: str | None = None,
    field: str | None = None,
    review_status: str | None = None,
    min_confidence: float | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Program).outerjoin(University)
    if country:
        query = query.filter(Program.country == country)
    if university:
        query = query.filter(University.name.ilike(f"%{university}%"))
    if field:
        query = query.filter(Program.field.ilike(f"%{field}%"))
    if review_status:
        query = query.filter(Program.review_status == review_status)
    if min_confidence is not None:
        query = query.filter(Program.extraction_confidence >= min_confidence)
    if search:
        query = query.filter(Program.program_name.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Program.extraction_confidence.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": [serialize_program(item) for item in items]}


@router.get("/review-queue")
def review_queue(db: Session = Depends(get_db)):
    rows = (
        db.query(Program)
        .outerjoin(University)
        .filter(Program.review_status.in_(["needs_review", "auto_extracted"]))
        .order_by(Program.extraction_confidence.asc(), Program.id.desc())
        .limit(100)
        .all()
    )
    return [serialize_program(row) for row in rows]


@router.get("/{program_id}")
def get_program(program_id: int, db: Session = Depends(get_db)):
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return serialize_program(program)


@router.put("/{program_id}")
def update_program(program_id: int, payload: dict, db: Session = Depends(get_db)):
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    for key, value in payload.items():
        if hasattr(program, key):
            setattr(program, key, value)
    db.commit()
    db.refresh(program)
    return serialize_program(program)


@router.post("/{program_id}/review")
def review_program(program_id: int, payload: dict, db: Session = Depends(get_db)):
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    program.review_status = payload.get("review_status", "reviewed")
    db.commit()
    return serialize_program(program)
