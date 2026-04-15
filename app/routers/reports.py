from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import CheckupEvent, LabResult, Report
from app.schemas import CompareRequest, CompareResponse, MarkerRecommendationResponse, ReportOut, ScheduleRequest, ScheduleResponse, UploadResponse
from app.services.calendar_service import create_calendar_event
from app.services.comparison import compare_lab_results, summarize_comparison
from app.services.lab_extractor import extract_lab_markers
from app.services.pdf_parser import extract_text
from app.services.recommendations import recommendation_for_marker

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/upload", response_model=UploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    report_date: date = Form(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_bytes = await file.read()
    stored_path = upload_dir / file.filename
    stored_path.write_bytes(file_bytes)

    raw_text = extract_text(file_bytes, file.filename)
    parsed_markers, warnings, confidence = extract_lab_markers(raw_text)

    report = Report(
        filename=file.filename,
        report_date=report_date,
        raw_text=raw_text,
        parse_confidence=confidence,
    )
    db.add(report)
    db.flush()

    for marker in parsed_markers:
        db.add(
            LabResult(
                report_id=report.id,
                marker_key=marker.marker_key,
                marker_label=marker.marker_label,
                value=marker.value,
                unit=marker.unit,
                reference_low=marker.reference_low,
                reference_high=marker.reference_high,
                raw_range=marker.raw_range,
                status=marker.status,
                raw_line=marker.raw_line,
            )
        )

    abnormal = [m for m in parsed_markers if m.status in {"low", "high"}]
    report.summary_text = (
        f"Parsed {len(parsed_markers)} markers from {file.filename}. "
        + (
            "Abnormal markers: " + ", ".join(f"{m.marker_label} ({m.status})" for m in abnormal[:8])
            if abnormal
            else "No parsed markers were outside their parsed ranges."
        )
    )

    db.commit()
    db.refresh(report)
    return UploadResponse(report=report, marker_count=len(parsed_markers), parse_warnings=warnings)


@router.get("", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.report_date.desc(), Report.uploaded_at.desc()).all()


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/compare", response_model=CompareResponse)
def compare_reports(payload: CompareRequest, db: Session = Depends(get_db)):
    report_a = db.query(Report).filter(Report.id == payload.report_id_a).first()
    report_b = db.query(Report).filter(Report.id == payload.report_id_b).first()

    if not report_a or not report_b:
        raise HTTPException(status_code=404, detail="One or both reports were not found")

    entries = compare_lab_results(report_a.results, report_b.results)
    return CompareResponse(
        report_id_a=report_a.id,
        report_id_b=report_b.id,
        overall_summary=summarize_comparison(entries),
        entries=entries,
    )


@router.get("/{report_id}/recommendation/{marker_key}", response_model=MarkerRecommendationResponse)
def marker_recommendation(report_id: str, marker_key: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    result = next((item for item in report.results if item.marker_key == marker_key), None)
    if not result:
        raise HTTPException(status_code=404, detail="Marker not found in report")

    return MarkerRecommendationResponse(
        report_id=report.id,
        marker_key=result.marker_key,
        marker_label=result.marker_label,
        value=result.value,
        unit=result.unit,
        status=result.status,
        recommendation=recommendation_for_marker(result, report.results),
    )


@router.post("/schedule-next-checkup", response_model=ScheduleResponse)
def schedule_next_checkup(payload: ScheduleRequest, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == payload.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    calendar_result = create_calendar_event(
        report.report_date,
        months_after=payload.months_after,
        reminder_days_before=payload.reminder_days_before,
    )

    event = CheckupEvent(
        report_id=report.id,
        scheduled_date=calendar_result["scheduled_date"],
        reminder_days_before=payload.reminder_days_before,
        calendar_event_id=calendar_result["calendar_event_id"],
        calendar_link=calendar_result["calendar_link"],
        status=calendar_result["status"],
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return ScheduleResponse(
        report_id=report.id,
        scheduled_date=event.scheduled_date,
        reminder_days_before=event.reminder_days_before,
        calendar_event_id=event.calendar_event_id,
        calendar_link=event.calendar_link,
        status=event.status,
    )
