from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class LabResultOut(BaseModel):
    id: int
    marker_key: str
    marker_label: str
    value: float
    unit: str = ""
    reference_low: float | None = None
    reference_high: float | None = None
    raw_range: str = ""
    status: str
    raw_line: str = ""

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: str
    filename: str
    report_date: date
    summary_text: str
    parse_confidence: float
    uploaded_at: datetime
    results: list[LabResultOut] = []

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    report: ReportOut
    marker_count: int
    parse_warnings: list[str] = []


class CompareRequest(BaseModel):
    report_id_a: str = Field(..., description="Older report id")
    report_id_b: str = Field(..., description="Newer report id")


class CompareEntry(BaseModel):
    marker_key: str
    marker_label: str
    previous_value: float | None = None
    current_value: float | None = None
    unit: str = ""
    delta: float | None = None
    previous_status: str | None = None
    current_status: str | None = None
    trend: str
    interpretation: str


class CompareResponse(BaseModel):
    report_id_a: str
    report_id_b: str
    overall_summary: str
    entries: list[CompareEntry]


class MarkerRecommendationResponse(BaseModel):
    marker_key: str
    marker_label: str
    report_id: str | None = None
    value: float | None = None
    unit: str = ""
    status: str = "unknown"
    recommendation: dict[str, Any]


class ScheduleRequest(BaseModel):
    report_id: str
    months_after: int = 6
    reminder_days_before: int = 14


class ScheduleResponse(BaseModel):
    report_id: str
    scheduled_date: date
    reminder_days_before: int
    calendar_event_id: str | None = None
    calendar_link: str | None = None
    status: str


class VapiWebhookResponse(BaseModel):
    results: list[dict[str, Any]]
