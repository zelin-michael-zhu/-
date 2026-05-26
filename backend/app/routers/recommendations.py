from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.recommendations.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/generate/{applicant_id}")
def generate_recommendations(applicant_id: int, provider: str = Query("mock"), db: Session = Depends(get_db)):
    return RecommendationService(db).generate(applicant_id, provider)


@router.get("/{applicant_id}")
def get_recommendations(applicant_id: int, db: Session = Depends(get_db)):
    return RecommendationService(db).latest(applicant_id)
