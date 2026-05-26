from fastapi import APIRouter
from app.services.ai.mock_ai_service import background_analysis, interview_prep, sop_outline

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/background-analysis")
def analyze_background():
    return background_analysis()


@router.post("/generate-sop-outline")
def generate_sop_outline():
    return sop_outline()


@router.post("/interview-prep")
def generate_interview_prep():
    return interview_prep()
