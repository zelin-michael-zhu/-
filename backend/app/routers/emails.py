from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import EmailItem

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("")
def list_emails(applicant_id: int | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(EmailItem)
    if applicant_id is not None:
        query = query.filter(EmailItem.applicant_id == applicant_id)
    return query.order_by(EmailItem.received_at.desc(), EmailItem.id.desc()).all()


@router.post("/analyze")
def analyze_emails():
    return {"status": "mock_analyzed", "message": "No real mailbox connection is used in MVP."}
