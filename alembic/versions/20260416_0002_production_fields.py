"""add production hardening report fields

Revision ID: 20260416_0002
Revises: 20260416_0001
Create Date: 2026-04-16 01:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260416_0002"
down_revision = "20260416_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "reports",
        sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "reports",
        sa.Column(
            "extraction_method",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'native-text'"),
        ),
    )
    op.create_index("ix_reports_user_report_date", "reports", ["user_id", "report_date"], unique=False)
    op.create_index("ix_lab_results_report_marker", "lab_results", ["report_id", "marker_key"], unique=False)
    op.create_index("ix_checkup_events_report_scheduled_date", "checkup_events", ["report_id", "scheduled_date"], unique=False)

    op.alter_column("reports", "ocr_used", server_default=None)
    op.alter_column("reports", "extraction_method", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_checkup_events_report_scheduled_date", table_name="checkup_events")
    op.drop_index("ix_lab_results_report_marker", table_name="lab_results")
    op.drop_index("ix_reports_user_report_date", table_name="reports")
    op.drop_column("reports", "extraction_method")
    op.drop_column("reports", "ocr_used")
