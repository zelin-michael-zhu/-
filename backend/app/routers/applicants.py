import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Applicant
from app.schemas.applicant import ApplicantUpdate
from app.services.matching.gpa_converter import convert_to_4

router = APIRouter(prefix="/applicants", tags=["applicants"])


def _demo_applicant() -> Applicant:
    return Applicant(
        full_name="Zeklin Zhu",
        email="demo@applypilot.local",
        university="BNU-HKBU United International College",
        college="School of Business",
        major="Business Analytics",
        degree="Bachelor",
        graduation_year=2027,
        gpa_value=3.62,
        gpa_scale=4.0,
        gpa_converted_4=convert_to_4(3.62, 4.0),
        ielts=7.0,
        target_countries_json=json.dumps(["Hong Kong", "Singapore", "United Kingdom"]),
        target_fields_json=json.dumps(["Business Analytics", "Finance", "FinTech", "Data Science"]),
        preference_priority="balanced",
    )


def _json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def analyze_profile(applicant: Applicant) -> dict:
    weighted_fields = [
        ("full_name", 6),
        ("email", 6),
        ("university", 8),
        ("major", 8),
        ("degree", 5),
        ("graduation_year", 5),
        ("gpa_value", 12),
        ("gpa_scale", 5),
        ("ielts", 10),
        ("target_countries_json", 10),
        ("target_fields_json", 10),
        ("experiences_json", 8),
        ("preference_priority", 7),
    ]
    score = 0
    for field, weight in weighted_fields:
        value = getattr(applicant, field)
        if value not in (None, "", "[]"):
            score += weight
    completeness = min(100, score)

    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []

    gpa = applicant.gpa_converted_4 or convert_to_4(applicant.gpa_value, applicant.gpa_scale)
    if gpa and gpa >= 3.6:
        strengths.append("Competitive GPA for selective taught master programs.")
    elif gpa:
        weaknesses.append("GPA may need careful program targeting.")
        suggestions.append("Balance reach, target, and safety programs based on GPA fit.")
    else:
        weaknesses.append("GPA is missing.")
        suggestions.append("Enter GPA and scale to unlock reliable matching.")

    if applicant.ielts and applicant.ielts >= 7:
        strengths.append("IELTS score meets a strong baseline.")
    elif applicant.toefl and applicant.toefl >= 100:
        strengths.append("TOEFL score meets a strong baseline.")
    else:
        weaknesses.append("Language score is missing or may need verification.")
        suggestions.append("Add IELTS or TOEFL scores and compare against official requirements.")

    target_fields = _json_list(applicant.target_fields_json)
    target_countries = _json_list(applicant.target_countries_json)
    if target_fields:
        strengths.append("Target fields are clear enough for program matching.")
    else:
        suggestions.append("Add target fields such as Business Analytics, Finance, or Data Science.")
    if target_countries:
        strengths.append("Country preferences are set.")
    else:
        suggestions.append("Add target countries to improve recommendation quality.")
    if not _json_list(applicant.experiences_json):
        weaknesses.append("Experiences are not detailed yet.")
        suggestions.append("Add internships, projects, research, or leadership experiences.")

    return {
        "profile_strength_score": min(100, completeness + (5 if gpa and gpa >= 3.6 else 0)),
        "completeness_percentage": completeness,
        "strengths": strengths[:5] or ["Basic profile has been started."],
        "weaknesses": weaknesses[:5],
        "suggested_improvements": suggestions[:5],
        "gpa_converted_4": applicant.gpa_converted_4,
    }


@router.get("/default")
def default_applicant(db: Session = Depends(get_db)):
    applicant = db.query(Applicant).order_by(Applicant.id).first()
    if not applicant:
        applicant = _demo_applicant()
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
    return applicant


@router.get("/{applicant_id}")
def get_applicant(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant


@router.put("/{applicant_id}")
def update_applicant(applicant_id: int, payload: ApplicantUpdate, db: Session = Depends(get_db)):
    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(applicant, key, value)
    applicant.gpa_converted_4 = convert_to_4(applicant.gpa_value, applicant.gpa_scale)
    db.commit()
    db.refresh(applicant)
    return applicant


@router.post("/{applicant_id}/analyze")
def analyze_applicant(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return analyze_profile(applicant)
