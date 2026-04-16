from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import Settings

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")



def sanitize_filename(filename: str) -> str:
    base = Path(filename).name
    cleaned = _SAFE_CHARS.sub("_", base).strip("._")
    return cleaned[:120] or "report"



def build_stored_filename(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return f"{uuid4().hex}{suffix}"



def validate_upload(file: UploadFile, file_bytes: bytes, settings: Settings) -> None:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.allowed_extensions:
        allowed = ", ".join(sorted(settings.allowed_extensions))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{suffix or 'unknown'}'. Allowed: {allowed}",
        )

    size_limit = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > size_limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large. Max size is {settings.max_upload_size_mb} MB.",
        )
