from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, default="")
    parse_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    results: Mapped[list["LabResult"]] = relationship(
        "LabResult",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="LabResult.marker_key",
    )
    checkups: Mapped[list["CheckupEvent"]] = relationship(
        "CheckupEvent",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="CheckupEvent.created_at.desc()",
    )


class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("reports.id"), nullable=False)
    marker_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    marker_label: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="")
    reference_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    reference_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_range: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="unknown")
    raw_line: Mapped[str] = mapped_column(Text, default="")

    report: Mapped["Report"] = relationship("Report", back_populates="results")


class CheckupEvent(Base):
    __tablename__ = "checkup_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("reports.id"), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    reminder_days_before: Mapped[int] = mapped_column(Integer, default=14)
    calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calendar_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report: Mapped["Report"] = relationship("Report", back_populates="checkups")
