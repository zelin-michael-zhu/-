from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import University
from app.schemas.university import UniversityCreate, UniversityOut

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("", response_model=list[UniversityOut])
def list_universities(db: Session = Depends(get_db)):
    return db.query(University).order_by(University.country, University.name).all()


@router.post("", response_model=UniversityOut)
def create_university(payload: UniversityCreate, db: Session = Depends(get_db)):
    item = University(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
