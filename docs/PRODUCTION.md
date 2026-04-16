# Production Hardening Notes

## PostgreSQL

- The app now supports PostgreSQL through SQLAlchemy with the `psycopg` driver.
- Use `postgresql+psycopg://...` for `DATABASE_URL`.
- CI runs Alembic against PostgreSQL before tests.

## Secrets

- Local development can still use `.env`.
- Production should use mounted secret files when possible.
- The app resolves auth and Vapi webhook secrets from mounted files first.

## OCR

- OCR fallback is optional and off by default.
- Enable with `OCR_ENABLED=true`.
- The Docker image includes OCRmyPDF and Tesseract.
- Use `scripts/backfill_ocr_reports.py` or `cloudrun/ocr-job.yaml` for historical OCR backfills.

## Request hardening

The app now includes:
- request-id headers
- readiness endpoint
- basic security headers
- basic in-memory rate limiting for auth, upload, and Vapi routes
- JSON logs option for production-style log ingestion
