import json
from app.models import Applicant, Program


def category(score: float) -> str:
    if score >= 85:
        return "Strong Target"
    if score >= 75:
        return "Target"
    if score >= 65:
        return "Safety"
    if score >= 50:
        return "Reach"
    return "Not Recommended"


def score_program(applicant: Applicant, program: Program) -> tuple[float, list[str], list[str]]:
    countries = json.loads(applicant.target_countries_json or "[]")
    fields = json.loads(applicant.target_fields_json or "[]")
    score = 0
    reasons: list[str] = []
    risks: list[str] = []
    gpa = applicant.gpa_converted_4 or applicant.gpa_value or 0
    if gpa >= 3.6:
        score += 30
        reasons.append("GPA is competitive for selective taught master programs.")
    elif gpa >= 3.2:
        score += 22
        reasons.append("GPA is broadly aligned with many program expectations.")
    else:
        score += 12
        risks.append("GPA may be below the typical competitive range.")
    if program.field and any(f.lower() in program.field.lower() for f in fields):
        score += 25
        reasons.append("Program field matches stated target fields.")
    else:
        score += 10
        risks.append("Field alignment is partial.")
    if program.country in countries:
        score += 15
        reasons.append("Country matches application preference.")
    if applicant.ielts and applicant.ielts >= 7:
        score += 15
        reasons.append("IELTS score meets a strong baseline.")
    elif applicant.toefl and applicant.toefl >= 100:
        score += 15
    else:
        score += 8
        risks.append("Language score should be verified against official requirement.")
    score += 12
    reasons.append("Business analytics background supports quantitative applications.")
    return min(score, 100), reasons, risks
