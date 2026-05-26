import json
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import AIRecommendation, Applicant, Program
from app.services.documents.document_service import DocumentService
from app.services.matching.matching_service import category, score_program


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def _candidate_programs(self) -> list[Program]:
        return (
            self.db.query(Program)
            .filter(or_(Program.review_status == "reviewed", (Program.review_status == "auto_extracted") & (Program.extraction_confidence >= 0.85)))
            .order_by(Program.extraction_confidence.desc(), Program.id.desc())
            .limit(30)
            .all()
        )

    def generate(self, applicant_id: int, provider: str = "mock") -> dict:
        applicant = self.db.get(Applicant, applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")
        docs = DocumentService(self.db)
        recommendations = []
        for program in self._candidate_programs():
            score, reasons, risks = score_program(applicant, program)
            missing = docs.missing_document_names_for_program(applicant_id, program.id)
            evidence_text = (program.raw_text_snapshot or program.description or "")[:500]
            recommendations.append({
                "program_id": program.id,
                "program_name": program.program_name,
                "university_name": program.university.name if program.university else None,
                "score": score,
                "category": category(score),
                "ai_reason": "Mock AI ranking uses rule score plus source-backed evidence. Verify with official website.",
                "risks": risks + (["Some fields are unknown and need verification."] if program.extraction_confidence and program.extraction_confidence < 0.9 else []),
                "missing_requirements": missing,
                "next_actions": ["Verify official requirements", "Prepare missing documents"] if missing else ["Verify official requirements", "Add to application list"],
                "evidence": [{"source_url": program.source_url, "text": evidence_text or "unknown"}],
            })
        recommendations.sort(key=lambda item: item["score"], reverse=True)
        payload = {
            "applicant_id": applicant_id,
            "generated_at": datetime.utcnow().isoformat(),
            "provider": provider,
            "recommendations": recommendations,
        }
        row = AIRecommendation(applicant_id=applicant_id, provider=provider, recommendations_json=json.dumps(payload, ensure_ascii=False))
        self.db.add(row)
        self.db.commit()
        return payload

    def latest(self, applicant_id: int) -> dict:
        row = (
            self.db.query(AIRecommendation)
            .filter(AIRecommendation.applicant_id == applicant_id)
            .order_by(AIRecommendation.id.desc())
            .first()
        )
        if not row:
            return {"applicant_id": applicant_id, "recommendations": []}
        return json.loads(row.recommendations_json or "{}")
