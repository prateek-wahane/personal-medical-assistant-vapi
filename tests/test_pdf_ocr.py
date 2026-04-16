from __future__ import annotations

from app.services.pdf_parser import ExtractedTextResult, extract_text_details


def test_pdf_parser_falls_back_to_ocr(monkeypatch):
    monkeypatch.setattr("app.services.pdf_parser._extract_pdf_text_native", lambda _bytes: "")
    monkeypatch.setattr(
        "app.services.pdf_parser.run_ocrmypdf",
        lambda _bytes: type("Result", (), {"text": "Hemoglobin 12.5 g/dL 13 - 17", "used_ocr": True, "method": "ocrmypdf", "warnings": []})(),
    )
    result = extract_text_details(b"%PDF-1.4 fake", "report.pdf")
    assert result.ocr_used is True
    assert result.method == "ocrmypdf"
    assert "Hemoglobin" in result.text


def test_pdf_parser_keeps_native_text_when_present(monkeypatch):
    monkeypatch.setattr("app.services.pdf_parser._extract_pdf_text_native", lambda _bytes: "Vitamin B12 260 pg/mL")
    result = extract_text_details(b"%PDF-1.4 fake", "report.pdf")
    assert result.ocr_used is False
    assert result.method == "native-text"
