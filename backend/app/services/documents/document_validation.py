import re
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

DOCUMENT_TYPES = {
    "CV": "CV",
    "Resume": "CV",
    "Personal Statement": "Personal Statement",
    "SOP": "Personal Statement",
    "Transcript": "Transcript",
    "Degree Certificate": "Degree Certificate",
    "IELTS": "IELTS",
    "TOEFL": "TOEFL",
    "GRE": "GRE",
    "GMAT": "GMAT",
    "Recommendation Letter": "Recommendation Letter",
    "Recommendation Letter 1": "Recommendation Letter",
    "Recommendation Letter 2": "Recommendation Letter",
    "Passport": "Passport",
    "Research Proposal": "Research Proposal",
    "Writing Sample": "Writing Sample",
    "Portfolio": "Portfolio",
    "Other": "Other",
    "Language Test Score": "IELTS",
}


def allowed_extensions() -> set[str]:
    return {item.strip().lower() for item in settings.document_allowed_extensions.split(",") if item.strip()}


def allowed_content_types() -> set[str]:
    return {item.strip().lower() for item in settings.document_allowed_content_types.split(",") if item.strip()}


def sanitize_filename(filename: str) -> str:
    name = Path(filename or "upload").name
    name = name.replace("\x00", "")
    stem = Path(name).stem
    suffix = Path(name).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    if not safe_stem:
        safe_stem = "document"
    return f"{safe_stem[:120]}{suffix}"


def validate_file_extension(filename: str) -> str:
    suffix = Path(filename or "").suffix.lower().lstrip(".")
    if suffix not in allowed_extensions():
        raise HTTPException(status_code=400, detail="File type not allowed")
    return suffix


def validate_content_type(content_type: str | None) -> str:
    normalized = (content_type or "").split(";")[0].strip().lower()
    if normalized not in allowed_content_types():
        raise HTTPException(status_code=400, detail="File content type not allowed")
    return normalized


def validate_file_size(size: int) -> None:
    max_bytes = settings.document_max_file_size_mb * 1024 * 1024
    if size <= 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if size > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")


def normalize_document_type(document_type: str) -> str:
    raw = " ".join((document_type or "").replace("_", " ").split())
    lowered = raw.lower()
    for key, value in DOCUMENT_TYPES.items():
        if key.lower() == lowered:
            return value
    title = raw.title()
    return DOCUMENT_TYPES.get(title, title)


def is_allowed_document_type(document_type: str) -> bool:
    return normalize_document_type(document_type) in set(DOCUMENT_TYPES.values())


async def read_and_validate_upload(file: UploadFile) -> bytes:
    validate_file_extension(file.filename or "")
    validate_content_type(file.content_type)
    data = await file.read()
    validate_file_size(len(data))
    return data
