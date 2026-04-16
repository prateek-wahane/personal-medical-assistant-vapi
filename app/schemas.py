from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


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
    user_id: str
    filename: str
    stored_filename: str
    content_type: str
    file_size_bytes: int
    ocr_used: bool
    extraction_method: str
    report_date: date
    summary_text: str
    parse_confidence: float
    uploaded_at: datetime
    results: list[LabResultOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    report: ReportOut
    marker_count: int
    parse_warnings: list[str] = Field(default_factory=list)


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
    months_after: int = Field(default=6, ge=1, le=24)
    reminder_days_before: int = Field(default=14, ge=1, le=60)


class ScheduleResponse(BaseModel):
    report_id: str
    scheduled_date: date
    reminder_days_before: int
    calendar_event_id: str | None = None
    calendar_link: str | None = None
    status: str


class VapiWebhookResponse(BaseModel):
    results: list[dict[str, Any]]
