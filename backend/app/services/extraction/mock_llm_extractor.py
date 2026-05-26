import re

from app.services.extraction.program_extraction_schema import ProgramExtraction

DOC_PATTERNS = {
    "CV": r"\b(cv|resume|curriculum vitae)\b",
    "Personal Statement": r"personal statement|statement of purpose|sop",
    "Transcript": r"transcript",
    "Degree Certificate": r"degree certificate|graduation certificate",
    "Recommendation Letter": r"recommendation|reference letter|referee",
    "Passport": r"passport",
}


def _field_from_text(text: str) -> str:
    lowered = text.lower()
    if "business analytics" in lowered or "analytics" in lowered:
        return "Business Analytics"
    if "data science" in lowered:
        return "Data Science"
    if "finance" in lowered:
        return "Finance"
    if "marketing" in lowered:
        return "Marketing"
    if "computer science" in lowered:
        return "Computer Science"
    return "Management"


def extract_program(text: str, source_url: str) -> ProgramExtraction:
    sample = text[:2500]
    lowered = text.lower()
    name_match = re.search(r"((MSc|MA|Master(?: of| in)?)[^\n]{3,90})", sample, re.I)
    ielts = re.search(r"IELTS[^\d]*(\d(?:\.\d)?)", text, re.I)
    toefl = re.search(r"TOEFL[^\d]*(\d{2,3})", text, re.I)
    tuition = re.search(r"(HKD|SGD|GBP|AUD|USD|£)\s?([0-9,]{4,})", text, re.I)
    deadline = re.search(r"(deadline|application deadline|closing date)[^\n:]*[:\s]+([A-Za-z0-9, ]{6,40})", text, re.I)
    program_name = name_match.group(1).strip() if name_match else "Auto-extracted Master Program"
    documents = [name for name, pattern in DOC_PATTERNS.items() if re.search(pattern, text, re.I)] or ["CV", "Transcript", "Personal Statement"]
    confidence = 0.82 if name_match and (ielts or tuition or deadline) else 0.62
    requirements = []
    if ielts:
        requirements.append({"requirement_type": "language", "requirement_name": "IELTS", "requirement_value": ielts.group(1), "required": True, "source_url": source_url})
    if toefl:
        requirements.append({"requirement_type": "language", "requirement_name": "TOEFL", "requirement_value": toefl.group(1), "required": True, "source_url": source_url})
    return ProgramExtraction(
        program_name=program_name,
        degree_type="MSc" if "msc" in program_name.lower() else "Master",
        field=_field_from_text(text),
        duration="1 year" if "one year" in lowered or "1 year" in lowered else None,
        study_mode="Full-time" if "full-time" in lowered or "full time" in lowered else None,
        tuition_amount=float(tuition.group(2).replace(",", "")) if tuition else None,
        tuition_currency="GBP" if tuition and tuition.group(1) == "£" else (tuition.group(1).upper() if tuition else None),
        application_deadline=deadline.group(2).strip() if deadline else None,
        deadline_note=deadline.group(0).strip() if deadline else None,
        program_url=source_url,
        source_evidence=[{"source_url": source_url, "text": sample[:600]}],
        ielts_requirement=ielts.group(1) if ielts else None,
        toefl_requirement=toefl.group(1) if toefl else None,
        gre_required="gre" in lowered and "not required" not in lowered,
        gmat_required="gmat" in lowered and "not required" not in lowered,
        work_experience_required="Required" if "work experience" in lowered and "not required" not in lowered else None,
        personal_statement_required=any(doc == "Personal Statement" for doc in documents),
        cv_required=any(doc == "CV" for doc in documents),
        transcript_required=any(doc == "Transcript" for doc in documents),
        recommendation_letters_required=2 if "recommendation" in lowered or "referee" in lowered else None,
        required_documents=documents,
        deadlines=[{"round_name": "Application Deadline", "deadline_text": deadline.group(2).strip(), "source_url": source_url}] if deadline else [],
        requirements=requirements,
        confidence=confidence,
        missing_fields=[] if confidence >= 0.75 else ["deadline", "tuition"],
    )
