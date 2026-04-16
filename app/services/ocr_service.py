from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from app.config import get_settings


class OCRServiceError(Exception):
    pass


@dataclass
class OCRResult:
    text: str
    used_ocr: bool
    method: str
    warnings: list[str] = field(default_factory=list)



def should_run_ocr(extracted_text: str) -> bool:
    settings = get_settings()
    meaningful_text = "".join(ch for ch in extracted_text if not ch.isspace())
    return settings.ocr_force or len(meaningful_text) < settings.ocr_min_extracted_chars



def run_ocrmypdf(file_bytes: bytes, *, language: str | None = None) -> OCRResult:
    settings = get_settings()
    warnings: list[str] = []
    if not settings.ocr_enabled:
        return OCRResult(text="", used_ocr=False, method="native-text", warnings=["OCR fallback is disabled."])

    command = shutil.which(settings.ocr_command)
    if not command:
        return OCRResult(text="", used_ocr=False, method="native-text", warnings=["OCRmyPDF is not installed in the runtime image."])

    language = language or settings.ocr_language

    with tempfile.TemporaryDirectory(prefix="ocr-report-") as tmpdir:
        input_path = Path(tmpdir) / "input.pdf"
        output_path = Path(tmpdir) / "output.pdf"
        input_path.write_bytes(file_bytes)

        cmd = [
            command,
            "--skip-text",
            "--force-ocr",
            "--language",
            language,
            str(input_path),
            str(output_path),
        ]

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.ocr_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise OCRServiceError("OCR timed out for this PDF.") from exc

        if completed.returncode != 0 or not output_path.exists():
            stderr = (completed.stderr or completed.stdout or "").strip()
            raise OCRServiceError(f"OCRmyPDF failed: {stderr[:240]}")

        from app.services.pdf_parser import _extract_pdf_text_native

        text = _extract_pdf_text_native(output_path.read_bytes())
        if not text.strip():
            warnings.append("OCR completed but produced very little text.")
        return OCRResult(text=text.strip(), used_ocr=True, method="ocrmypdf", warnings=warnings)
