from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import get_settings

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class CalendarServiceError(Exception):
    pass


def calculate_next_checkup_date(report_date, months_after: int = 6):
    return report_date + relativedelta(months=months_after)


def _load_credentials() -> Credentials:
    settings = get_settings()
    token_path = Path(settings.google_token_file)

    if not token_path.exists():
        raise CalendarServiceError(
            f"Google token file not found at {token_path}. Run scripts/google_calendar_auth.py first."
        )

    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds
    except Exception as exc:  # pragma: no cover - defensive catch around Google SDK
        raise CalendarServiceError("Unable to load Google Calendar credentials.") from exc


def create_calendar_event(report_date, months_after: int = 6, reminder_days_before: int = 14):
    settings = get_settings()
    creds = _load_credentials()

    if months_after < 1:
        raise CalendarServiceError("months_after must be at least 1.")
    if reminder_days_before < 1:
        raise CalendarServiceError("reminder_days_before must be at least 1.")

    next_date = calculate_next_checkup_date(report_date, months_after)
    start_dt = datetime(next_date.year, next_date.month, next_date.day, 9, 0, 0)
    end_dt = start_dt + timedelta(minutes=30)

    event_body = {
        "summary": "Blood Checkup",
        "description": (
            "Follow-up blood check scheduled automatically from your previous report. "
            "Bring previous reports and discuss any abnormal markers with your clinician."
        ),
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": settings.timezone,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": settings.timezone,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": reminder_days_before * 24 * 60},
            ],
        },
    }

    try:
        service = build("calendar", "v3", credentials=creds)
        created = service.events().insert(calendarId=settings.google_calendar_id, body=event_body).execute()
    except HttpError as exc:
        raise CalendarServiceError("Google Calendar rejected the event request.") from exc
    except Exception as exc:  # pragma: no cover - defensive catch around Google SDK
        raise CalendarServiceError("Unexpected calendar integration failure.") from exc

    return {
        "scheduled_date": next_date,
        "calendar_event_id": created.get("id"),
        "calendar_link": created.get("htmlLink"),
        "status": "scheduled",
    }
