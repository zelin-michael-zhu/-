import json
from datetime import date, datetime
from app.core.database import SessionLocal
from app.models import Applicant, Application, Document, EmailItem, Program, University
from app.services.matching.gpa_converter import convert_to_4
from app.scripts.seed_universities import seed_universities

PROGRAMS = [
    ("HKU", "HKU MSc Business Analytics", "Business Analytics", "Hong Kong", "HKD", 396000, "2026-12-01", "https://www.hku.hk/msc-business-analytics"),
    ("NUS", "NUS MSc Business Analytics", "Business Analytics", "Singapore", "SGD", 65000, "2026-11-30", "https://www.nus.edu.sg/msc-business-analytics"),
    ("CUHK", "CUHK MSc Finance", "Finance", "Hong Kong", "HKD", 420000, "2027-01-15", "https://www.cuhk.edu.hk/msc-finance"),
    ("UCL", "UCL MSc Management", "Management", "United Kingdom", "GBP", 38300, "2027-03-31", "https://www.ucl.ac.uk/msc-management"),
    ("Imperial", "Imperial MSc Strategic Marketing", "Marketing", "United Kingdom", "GBP", 41000, "2027-02-15", "https://www.imperial.ac.uk/msc-strategic-marketing"),
    ("Manchester", "University of Manchester MSc Business Analytics", "Business Analytics", "United Kingdom", "GBP", 31000, "2027-01-05", "https://www.manchester.ac.uk/msc-business-analytics"),
    ("NTU", "NTU MSc Finance", "Finance", "Singapore", "SGD", 71940, "2026-12-31", "https://www.ntu.edu.sg/msc-finance"),
    ("SMU", "SMU MSc Applied Finance", "Finance", "Singapore", "SGD", 56880, "2027-01-20", "https://www.smu.edu.sg/msc-applied-finance"),
]

DOCS = ["CV", "Personal Statement", "Transcript", "Degree Certificate", "IELTS", "GRE", "Recommendation Letter 1", "Recommendation Letter 2", "Passport", "Research Proposal"]


def seed_demo_data(db) -> dict:
    seed_universities(db)
    applicant = db.query(Applicant).filter(Applicant.email == "demo@applypilot.local").first()
    if not applicant:
        applicant = Applicant(
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
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
    inserted_programs = 0
    for short, name, field, country, currency, tuition, deadline, url in PROGRAMS:
        uni = db.query(University).filter(University.short_name == short).first()
        if not db.query(Program).filter(Program.program_name == name).first():
            db.add(Program(university_id=uni.id if uni else None, program_name=name, normalized_program_name=name.lower(), degree_type="MSc", field=field, country=country, city=uni.city if uni else None, duration="1 year", study_mode="Full-time", tuition_amount=tuition, tuition_currency=currency, application_deadline=date.fromisoformat(deadline), source_url=url, program_url=url, description="Demo seeded program for local MVP browsing. Auto-extracted data, please verify with official website.", ielts_requirement="7.0", toefl_requirement="100", gre_required=False, gmat_required=False, recommendation_letters_required=2, personal_statement_required=True, cv_required=True, transcript_required=True, raw_text_snapshot="Demo raw text snapshot. Verify with official website before applying.", extraction_confidence=0.86, review_status="auto_extracted", last_checked=datetime.utcnow()))
            inserted_programs += 1
    db.commit()
    for idx, doc in enumerate(DOCS):
        if not db.query(Document).filter(Document.applicant_id == applicant.id, Document.name == doc).first():
            db.add(Document(applicant_id=applicant.id, name=doc, type=doc.lower().replace(" ", "_"), status=["ready", "draft", "missing", "submitted"][idx % 4], last_updated=datetime.utcnow()))
    for program in db.query(Program).limit(4).all():
        if not db.query(Application).filter(Application.applicant_id == applicant.id, Application.program_id == program.id).first():
            db.add(Application(applicant_id=applicant.id, program_id=program.id, status=["Not Started", "In Progress", "Submitted", "Interview"][program.id % 4], deadline=program.application_deadline, missing_items_json=json.dumps(["SOP", "Recommendation Letter"])))
    emails = [
        ("admissions@nus.edu.sg", "NUS interview invitation", "Urgent", "Schedule interview within 5 days."),
        ("admissions@hku.hk", "HKU missing transcript request", "Urgent", "Upload official transcript."),
        ("ucl@example.ac.uk", "UCL application submitted confirmation", "Updates", "Application received."),
        ("cuhk@example.edu.hk", "CUHK referee submitted confirmation", "No Action Needed", "Reference submitted."),
    ]
    for sender, subject, category, action in emails:
        if not db.query(EmailItem).filter(EmailItem.subject == subject).first():
            db.add(EmailItem(applicant_id=applicant.id, sender=sender, subject=subject, body_preview=subject, category=category, ai_summary=f"Mock summary: {subject}", suggested_action=action, received_at=datetime.utcnow()))
    db.commit()
    return {"applicant_id": applicant.id, "inserted_programs": inserted_programs}


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print(seed_demo_data(db))
    finally:
        db.close()
