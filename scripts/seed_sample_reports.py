from __future__ import annotations

from datetime import date

from app.db import SessionLocal
from app.models import LabResult, Report, User
from app.services.auth import hash_password

SAMPLES = [
    {
        "filename": "sample_report_old.txt",
        "stored_filename": "seed_sample_report_old.txt",
        "report_date": date(2025, 10, 15),
        "summary_text": "Older baseline report with low hemoglobin and low ferritin.",
        "markers": [
            ("hemoglobin", "Hemoglobin", 11.2, "g/dL", 13.0, 17.0, "13.0-17.0", "low"),
            ("ferritin", "Ferritin", 11.0, "ng/mL", 30.0, 400.0, "30-400", "low"),
            ("ldl", "LDL", 144.0, "mg/dL", 0.0, 100.0, "0-100", "high"),
        ],
    },
    {
        "filename": "sample_report_new.txt",
        "stored_filename": "seed_sample_report_new.txt",
        "report_date": date(2026, 4, 15),
        "summary_text": "Newer report with improved hemoglobin and ferritin but LDL still elevated.",
        "markers": [
            ("hemoglobin", "Hemoglobin", 12.7, "g/dL", 13.0, 17.0, "13.0-17.0", "low"),
            ("ferritin", "Ferritin", 22.0, "ng/mL", 30.0, 400.0, "30-400", "low"),
            ("ldl", "LDL", 136.0, "mg/dL", 0.0, 100.0, "0-100", "high"),
        ],
    },
]


def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if not user:
            user = User(email="demo@example.com", password_hash=hash_password("demo-password"))
            db.add(user)
            db.flush()

        for sample in SAMPLES:
            report = Report(
                user_id=user.id,
                filename=sample["filename"],
                stored_filename=sample["stored_filename"],
                content_type="text/plain",
                file_size_bytes=0,
                ocr_used=False,
                extraction_method="plain-text",
                report_date=sample["report_date"],
                summary_text=sample["summary_text"],
                parse_confidence=0.9,
                raw_text=sample["summary_text"],
            )
            db.add(report)
            db.flush()

            for marker_key, marker_label, value, unit, low, high, raw_range, status in sample["markers"]:
                db.add(
                    LabResult(
                        report_id=report.id,
                        marker_key=marker_key,
                        marker_label=marker_label,
                        value=value,
                        unit=unit,
                        reference_low=low,
                        reference_high=high,
                        raw_range=raw_range,
                        status=status,
                        raw_line=f"{marker_label} {value} {unit} {raw_range}",
                    )
                )
        db.commit()
        print("Seeded sample reports for demo@example.com (password: demo-password)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
