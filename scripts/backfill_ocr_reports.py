from __future__ import annotations

import argparse
from pathlib import Path

from app.db import SessionLocal
from app.models import Report
from app.services.pdf_parser import extract_text_details


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill OCR text for existing PDF reports.")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        reports = (
            db.query(Report)
            .filter(Report.content_type.like("application/pdf%"))
            .order_by(Report.uploaded_at.desc())
            .limit(args.limit)
            .all()
        )
        for report in reports:
            path = Path("./uploads") / report.stored_filename
            if not path.exists():
                print(f"skip missing file {report.stored_filename}")
                continue
            extraction = extract_text_details(path.read_bytes(), report.filename)
            report.raw_text = extraction.text
            report.ocr_used = extraction.ocr_used
            report.extraction_method = extraction.method
            print(f"processed {report.id} -> {report.extraction_method}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
