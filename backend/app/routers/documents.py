from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.documents.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(applicant_id: int | None = Query(None), db: Session = Depends(get_db)):
    if applicant_id is None:
        return []
    return DocumentService(db).list_documents(applicant_id)


@router.post("")
def create_document(payload: dict, db: Session = Depends(get_db)):
    # Compatibility endpoint for older UI/tests: creates metadata-only document records.
    from app.models import Document
    from datetime import datetime

    now = datetime.utcnow()
    item = Document(
        applicant_id=payload.get("applicant_id"),
        name=payload.get("name") or payload.get("type") or "Other",
        type=payload.get("type") or payload.get("name") or "Other",
        status=payload.get("status", "missing"),
        file_path=payload.get("file_path"),
        notes=payload.get("notes"),
        last_updated=now,
        is_active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return DocumentService(db).list_documents(item.applicant_id or 0)


@router.post("/upload")
async def upload_document(
    applicant_id: int = Form(...),
    document_type: str = Form(...),
    notes: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await DocumentService(db).upload_document(applicant_id, document_type, file, notes)


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    path, filename, content_type = DocumentService(db).get_download_path(document_id)
    return FileResponse(path, media_type=content_type, filename=filename)


@router.put("/{document_id}/status")
def update_document_status(document_id: int, payload: dict, db: Session = Depends(get_db)):
    return DocumentService(db).update_document_status(document_id, payload.get("status", "missing"))


@router.put("/{document_id}")
def update_document(document_id: int, payload: dict, db: Session = Depends(get_db)):
    return DocumentService(db).update_document(document_id, payload)


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    return DocumentService(db).delete_document(document_id)


@router.post("/checklist/{program_id}")
def checklist(program_id: int, payload: dict, db: Session = Depends(get_db)):
    return DocumentService(db).generate_checklist(payload.get("applicant_id"), program_id)
