import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.models import Document
from app.services.documents.document_validation import sanitize_filename


@dataclass
class StorageResult:
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str | None
    file_size: int
    file_hash: str


def storage_root() -> Path:
    root = Path(settings.document_storage_dir)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[3] / root
    return root.resolve()


def ensure_storage_dirs() -> Path:
    root = storage_root()
    root.mkdir(parents=True, exist_ok=True)
    return root


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_type_dir(document_type: str) -> str:
    return sanitize_filename(document_type).replace(".", "_")


def save_upload_bytes(applicant_id: int, document_type: str, file: UploadFile, data: bytes, version: int) -> StorageResult:
    root = ensure_storage_dirs()
    safe_original = sanitize_filename(file.filename or "document")
    stored_filename = f"v{version}_{safe_original}"
    target_dir = root / "applicants" / str(applicant_id) / _safe_type_dir(document_type)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = (target_dir / stored_filename).resolve()
    if not str(target_path).startswith(str(root)):
        raise HTTPException(status_code=400, detail="Invalid storage path")
    target_path.write_bytes(data)
    return StorageResult(
        original_filename=file.filename or safe_original,
        stored_filename=stored_filename,
        file_path=str(target_path),
        content_type=file.content_type,
        file_size=len(data),
        file_hash=compute_sha256(data),
    )


def get_document_path(document: Document) -> Path:
    if not document.file_path:
        raise HTTPException(status_code=404, detail="Document file path is missing")
    path = Path(document.file_path).resolve()
    root = storage_root()
    if not str(path).startswith(str(root)):
        raise HTTPException(status_code=400, detail="Document path is outside storage root")
    return path


def delete_document_file(document: Document) -> None:
    path = get_document_path(document)
    if not path.exists():
        return
    archive_dir = path.parent / "archived"
    archive_dir.mkdir(exist_ok=True)
    shutil.move(str(path), str(archive_dir / path.name))
