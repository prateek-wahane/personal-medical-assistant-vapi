from datetime import date

from app.db import SessionLocal
from app.models import LabResult, Report


SAMPLES = [
    {
        "filename": "sample_report_old.txt",
        "report_date": date(2025, 10, 15),
        "summary_text": "Older baseline report with low hemoglobin and low ferritin.",
        "markers": [
            ("hemoglobin", "Hemoglobin", 11.2, "g/dL", 13.0, 17.0, "13-17", "low", "Hemoglobin 11.2 g/dL 13-17"),
            ("ferritin", "Ferritin", 12.0, "ng/mL", 30.0, 400.0, "30-400", "low", "Ferritin 12 ng/mL 30-400"),
            ("vitamin_b12", "Vitamin B12", 260.0, "pg/mL", 200.0, 900.0, "200-900", "normal", "Vitamin B12 260 pg/mL 200-900"),
            ("hba1c", "HbA1c", 5.8, "%", 4.0, 5.6, "4.0-5.6", "high", "HbA1c 5.8 % 4.0-5.6"),
            ("ldl", "LDL", 142.0, "mg/dL", 0.0, 100.0, "<100", "high", "LDL 142 mg/dL <100"),
        ],
    },
    {
        "filename": "sample_report_new.txt",
        "report_date": date(2026, 4, 15),
        "summary_text": "Newer report with improved hemoglobin and ferritin but LDL still elevated.",
        "markers": [
            ("hemoglobin", "Hemoglobin", 12.5, "g/dL", 13.0, 17.0, "13-17", "low", "Hemoglobin 12.5 g/dL 13-17"),
            ("ferritin", "Ferritin", 24.0, "ng/mL", 30.0, 400.0, "30-400", "low", "Ferritin 24 ng/mL 30-400"),
            ("vitamin_b12", "Vitamin B12", 340.0, "pg/mL", 200.0, 900.0, "200-900", "normal", "Vitamin B12 340 pg/mL 200-900"),
            ("hba1c", "HbA1c", 5.5, "%", 4.0, 5.6, "4.0-5.6", "normal", "HbA1c 5.5 % 4.0-5.6"),
            ("ldl", "LDL", 136.0, "mg/dL", 0.0, 100.0, "<100", "high", "LDL 136 mg/dL <100"),
        ],
    },
]


def main():
    db = SessionLocal()
    try:
        for sample in SAMPLES:
            report = Report(
                filename=sample["filename"],
                report_date=sample["report_date"],
                summary_text=sample["summary_text"],
                parse_confidence=0.9,
                raw_text=sample["summary_text"],
            )
            db.add(report)
            db.flush()

            for marker in sample["markers"]:
                db.add(
                    LabResult(
                        report_id=report.id,
                        marker_key=marker[0],
                        marker_label=marker[1],
                        value=marker[2],
                        unit=marker[3],
                        reference_low=marker[4],
                        reference_high=marker[5],
                        raw_range=marker[6],
                        status=marker[7],
                        raw_line=marker[8],
                    )
                )
        db.commit()
        print("Seeded sample reports.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
