from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.services.ocr_service import OCRResult, OCRServiceError, run_ocrmypdf, should_run_ocr


@dataclass
class ExtractedTextResult:
    text: str
    method: str
    ocr_used: bool
    warnings: list[str] = field(default_factory=list)


def _extract_pdf_text_native(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def extract_text_details(file_bytes: bytes, filename: str) -> ExtractedTextResult:
    suffix = Path(filename).suffix.lower()
    if suffix != ".pdf":
        return ExtractedTextResult(
            text=file_bytes.decode("utf-8", errors="ignore").strip(),
            method="plain-text",
            ocr_used=False,
        )

    native_text = _extract_pdf_text_native(file_bytes)
    warnings: list[str] = []
    if not should_run_ocr(native_text):
        return ExtractedTextResult(text=native_text, method="native-text", ocr_used=False, warnings=warnings)

    try:
        ocr_result: OCRResult = run_ocrmypdf(file_bytes)
        warnings.extend(ocr_result.warnings)
        if ocr_result.used_ocr and ocr_result.text.strip():
            warnings.append("OCR fallback was used for this report.")
            return ExtractedTextResult(
                text=ocr_result.text,
                method=ocr_result.method,
                ocr_used=True,
                warnings=warnings,
            )
    except OCRServiceError as exc:
        warnings.append(str(exc))

    if not native_text.strip():
        warnings.append("Native PDF extraction returned very little text and OCR did not recover usable text.")
    return ExtractedTextResult(text=native_text, method="native-text", ocr_used=False, warnings=warnings)


def extract_text(file_bytes: bytes, filename: str) -> str:
    return extract_text_details(file_bytes, filename).text
