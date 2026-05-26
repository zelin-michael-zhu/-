import pytest
from fastapi import HTTPException

from app.services.documents.document_validation import sanitize_filename, validate_file_extension, validate_file_size


def test_rejects_dangerous_extensions():
    for filename in ["run.exe", "script.js", "page.html", "shell.sh", "tool.py"]:
        with pytest.raises(HTTPException):
            validate_file_extension(filename)


def test_rejects_large_file(monkeypatch):
    from app.services.documents import document_validation

    monkeypatch.setattr(document_validation.settings, "document_max_file_size_mb", 1)
    with pytest.raises(HTTPException):
        validate_file_size(2 * 1024 * 1024)


def test_sanitize_filename_prevents_path_traversal():
    assert sanitize_filename("../../secret.pdf") == "secret.pdf"
    assert ".." not in sanitize_filename("my ../ cv.pdf")
