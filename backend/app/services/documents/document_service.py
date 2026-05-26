import json
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import Applicant, Document, Program, ProgramDocument
from app.services.documents.document_storage import delete_document_file, get_document_path, save_upload_bytes
from app.services.documents.document_validation import is_allowed_document_type, normalize_document_type, read_and_validate_upload

VALID_STATUSES = {"missing", "draft", "ready", "submitted", "deleted"}
DEFAULT_REQUIRED_DOCUMENTS = [
    "CV",
    "Personal Statement",
    "Transcript",
    "Degree Certificate",
    "IELTS",
    "Recommendation Letter",
    "Passport",
]


def serialize_document(document: Document) -> dict:
    data = {c.name: getattr(document, c.name) for c in document.__table__.columns}
    data["download_url"] = f"/api/documents/{document.id}/download" if document.file_path and document.is_active else None
    data["file_exists"] = bool(document.file_path and Path(document.file_path).exists())
    return data


def _normalize_key(value: str) -> str:
    return normalize_document_type(value).lower()


def _required_documents_for_program(db: Session, program_id: int) -> list[dict]:
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    rows = db.query(ProgramDocument).filter(ProgramDocument.program_id == program_id, ProgramDocument.required.is_(True)).all()
    if rows:
        return [
            {
                "document_type": normalize_document_type(row.document_type),
                "required": row.required,
                "quantity": row.quantity or 1,
                "description": row.description,
                "source_url": row.source_url or program.source_url,
            }
            for row in rows
        ]
    fallback = []
    if program.cv_required:
        fallback.append("CV")
    if program.personal_statement_required:
        fallback.append("Personal Statement")
    if program.transcript_required:
        fallback.append("Transcript")
    if program.recommendation_letters_required:
        fallback.append("Recommendation Letter")
    if program.ielts_requirement or program.toefl_requirement or program.language_requirement:
        fallback.append("IELTS")
    if not fallback:
        fallback = DEFAULT_REQUIRED_DOCUMENTS
    return [{"document_type": item, "required": True, "quantity": 1, "description": item, "source_url": program.source_url} for item in fallback]


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def list_documents(self, applicant_id: int, include_inactive: bool = False) -> list[dict]:
        query = self.db.query(Document).filter(Document.applicant_id == applicant_id)
        if not include_inactive:
            query = query.filter(Document.is_active.is_(True))
        rows = query.order_by(Document.type.asc(), Document.version.desc(), Document.id.desc()).all()
        latest: dict[str, Document] = {}
        for row in rows:
            key = _normalize_key(row.type)
            if include_inactive or key not in latest:
                latest[key] = row
        return [serialize_document(item) for item in latest.values()]

    def get_latest_documents_by_type(self, applicant_id: int) -> dict[str, Document]:
        rows = (
            self.db.query(Document)
            .filter(Document.applicant_id == applicant_id, Document.is_active.is_(True))
            .order_by(Document.type.asc(), Document.version.desc(), Document.id.desc())
            .all()
        )
        latest: dict[str, Document] = {}
        for row in rows:
            key = _normalize_key(row.type)
            if key not in latest:
                latest[key] = row
        return latest

    async def upload_document(self, applicant_id: int, document_type: str, file: UploadFile, notes: str | None = None) -> dict:
        applicant = self.db.get(Applicant, applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")
        normalized_type = normalize_document_type(document_type)
        if not is_allowed_document_type(normalized_type):
            raise HTTPException(status_code=400, detail="Unsupported document type")
        data = await read_and_validate_upload(file)
        previous = (
            self.db.query(Document)
            .filter(Document.applicant_id == applicant_id, Document.type == normalized_type)
            .order_by(Document.version.desc())
            .first()
        )
        version = (previous.version if previous else 0) + 1
        self.db.query(Document).filter(Document.applicant_id == applicant_id, Document.type == normalized_type, Document.is_active.is_(True)).update({"is_active": False})
        storage = save_upload_bytes(applicant_id, normalized_type, file, data, version)
        now = datetime.utcnow()
        document = Document(
            applicant_id=applicant_id,
            name=normalized_type,
            type=normalized_type,
            status="ready",
            file_path=storage.file_path,
            original_filename=storage.original_filename,
            stored_filename=storage.stored_filename,
            content_type=storage.content_type,
            file_size=storage.file_size,
            file_hash=storage.file_hash,
            version=version,
            notes=notes,
            uploaded_at=now,
            last_updated=now,
            is_active=True,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return serialize_document(document)

    def update_document_status(self, document_id: int, status: str) -> dict:
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid document status")
        document = self.db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        document.status = status
        document.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return serialize_document(document)

    def update_document(self, document_id: int, payload: dict) -> dict:
        document = self.db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if "status" in payload and payload["status"] not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid document status")
        for key in ["status", "notes", "used_by_json"]:
            if key in payload:
                setattr(document, key, payload[key])
        document.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return serialize_document(document)

    def delete_document(self, document_id: int, archive_file: bool = False) -> dict:
        document = self.db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if archive_file and document.file_path:
            delete_document_file(document)
        document.is_active = False
        document.status = "deleted"
        document.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return serialize_document(document)

    def get_download_path(self, document_id: int) -> tuple[Path, str, str | None]:
        document = self.db.get(Document, document_id)
        if not document or not document.is_active:
            raise HTTPException(status_code=404, detail="Document not found")
        path = get_document_path(document)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        return path, document.original_filename or path.name, document.content_type

    def generate_checklist(self, applicant_id: int, program_id: int) -> dict:
        required = _required_documents_for_program(self.db, program_id)
        latest = self.get_latest_documents_by_type(applicant_id)
        ready: list[dict] = []
        missing: list[dict] = []
        submitted: list[dict] = []
        for item in required:
            key = _normalize_key(item["document_type"])
            document = latest.get(key)
            payload = {"required": item, "document": serialize_document(document) if document else None}
            if document and document.status == "submitted":
                submitted.append(payload)
            elif document and document.status == "ready":
                ready.append(payload)
            else:
                missing.append(payload)
        warnings = ["Verify every requirement with the official program website before applying."]
        if missing:
            warnings.insert(0, "Some required documents are missing or not ready.")
        return {
            "program_id": program_id,
            "applicant_id": applicant_id,
            "required_documents": required,
            "ready_documents": ready,
            "missing_documents": missing,
            "submitted_documents": submitted,
            "warnings": warnings,
        }

    def get_document_availability_for_program(self, applicant_id: int, program_id: int) -> dict:
        checklist = self.generate_checklist(applicant_id, program_id)
        return {
            "available_documents": {
                (item["required"]["document_type"]): {
                    "status": item["document"]["status"],
                    "file_path": item["document"]["file_path"],
                    "file_exists": item["document"]["file_exists"],
                }
                for item in checklist["ready_documents"] + checklist["submitted_documents"]
                if item.get("document")
            },
            "missing_documents": [item["required"]["document_type"] for item in checklist["missing_documents"]],
            "warnings": checklist["warnings"],
        }

    def missing_document_names_for_program(self, applicant_id: int, program_id: int) -> list[str]:
        checklist = self.generate_checklist(applicant_id, program_id)
        return [item["required"]["document_type"] for item in checklist["missing_documents"]]
