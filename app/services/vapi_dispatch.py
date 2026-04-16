from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import CheckupEvent, Report
from app.services.calendar_service import CalendarServiceError, create_calendar_event
from app.services.comparison import compare_lab_results, summarize_comparison
from app.services.recommendations import recommendation_for_marker


def _latest_report(db: Session, user_id: str | None = None) -> Report | None:
    query = db.query(Report)
    if user_id:
        query = query.filter(Report.user_id == user_id)
    return query.order_by(Report.report_date.desc(), Report.uploaded_at.desc()).first()


def _scoped_report(db: Session, report_id: str | None, user_id: str | None) -> Report | None:
    if report_id:
        query = db.query(Report).filter(Report.id == report_id)
        if user_id:
            query = query.filter(Report.user_id == user_id)
        return query.first()
    return _latest_report(db, user_id=user_id)


def handle_tool_call(db: Session, tool_name: str, arguments: dict, *, user_id: str | None = None) -> dict:
    if not user_id:
        return {"message": "User context is required for Vapi tool calls. Pass userId in assistant metadata or variable values."}

    if tool_name == "get_latest_report_summary":
        report = _latest_report(db, user_id=user_id)
        if not report:
            return {"message": "No reports are available yet for this user. Please upload a blood report first."}
        return {
            "report_id": report.id,
            "report_date": report.report_date.isoformat(),
            "summary": report.summary_text,
        }

    if tool_name == "compare_reports":
        old_report = _scoped_report(db, arguments.get("report_id_a"), user_id)
        new_report = _scoped_report(db, arguments.get("report_id_b"), user_id)

        if not old_report or not new_report:
            reports_query = db.query(Report)
            if user_id:
                reports_query = reports_query.filter(Report.user_id == user_id)
            reports = reports_query.order_by(Report.report_date.desc()).limit(2).all()
            if len(reports) < 2:
                return {"message": "Two reports are needed for comparison."}
            new_report, old_report = reports[0], reports[1]

        entries = compare_lab_results(old_report.results, new_report.results)
        return {
            "report_id_a": old_report.id,
            "report_id_b": new_report.id,
            "overall_summary": summarize_comparison(entries),
            "entries": entries,
        }

    if tool_name == "get_marker_recommendation":
        report = _scoped_report(db, arguments.get("report_id"), user_id)
        marker_key = arguments.get("marker_key")
        if not report:
            return {"message": "No report found for recommendation."}
        if not marker_key:
            return {"message": "marker_key is required."}

        marker = next((item for item in report.results if item.marker_key == marker_key), None)
        if not marker:
            return {"message": f"Marker '{marker_key}' was not found in the selected report."}

        return {
            "report_id": report.id,
            "marker_key": marker.marker_key,
            "marker_label": marker.marker_label,
            "value": marker.value,
            "unit": marker.unit,
            "status": marker.status,
            "recommendation": recommendation_for_marker(marker, report.results),
        }

    if tool_name == "schedule_next_checkup":
        report = _scoped_report(db, arguments.get("report_id"), user_id)
        months_after = int(arguments.get("months_after", 6))
        reminder_days_before = int(arguments.get("reminder_days_before", 14))
        if not report:
            return {"message": "No report found to schedule the next checkup."}

        try:
            calendar_result = create_calendar_event(
                report.report_date,
                months_after=months_after,
                reminder_days_before=reminder_days_before,
            )
        except CalendarServiceError as exc:
            return {"message": str(exc)}

        event = CheckupEvent(
            report_id=report.id,
            scheduled_date=calendar_result["scheduled_date"],
            reminder_days_before=reminder_days_before,
            calendar_event_id=calendar_result["calendar_event_id"],
            calendar_link=calendar_result["calendar_link"],
            status=calendar_result["status"],
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return {
            "report_id": report.id,
            "scheduled_date": str(event.scheduled_date),
            "reminder_days_before": event.reminder_days_before,
            "calendar_event_id": event.calendar_event_id,
            "calendar_link": event.calendar_link,
            "status": event.status,
        }

    return {"message": f"Unsupported tool: {tool_name}"}
