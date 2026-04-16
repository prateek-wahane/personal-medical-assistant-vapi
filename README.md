# Personal Medical Assistant with Vapi

A production-oriented starter project for a **voice-based personal medical assistant** that can:
- upload and parse blood reports
- compare report trends over time
- provide educational nutrition and lifestyle guidance
- schedule the next blood checkup **6 months later**
- create a Google Calendar event with a **14-day reminder**
- expose **Vapi custom tool** and **custom knowledge-base** endpoints
- isolate each user’s reports with login-based access control

## What changed in this production pass

- PostgreSQL-ready SQLAlchemy engine settings and CI migration smoke tests
- secret-file support for Cloud Run / Secret Manager style mounts
- OCR fallback for scanned PDFs using **OCRmyPDF + Tesseract**
- request-id headers, structured-log option, readiness endpoint, security headers, and basic rate limiting
- Cloud Run service and OCR job templates
- Docker image updated with OCR runtime dependencies

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Open:
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Ready: `http://localhost:8000/ready`
- Frontend: open `frontend/index.html`

## Production quick start with PostgreSQL

```bash
docker compose -f docker-compose.prod.yml up --build
```

This starts:
- PostgreSQL 16
- the API container with Alembic migration on boot
- OCR runtime dependencies preinstalled in the image

## First-use flow

1. Register a user with `POST /api/auth/register`
2. Login with `POST /api/auth/login`
3. Use the returned bearer token for report APIs
4. Upload one or two reports
5. Compare reports and request marker guidance
6. Authenticate Google Calendar and schedule the next checkup
7. Connect Vapi with the current user id in assistant metadata or variable values

## Demo seed user

After running:

```bash
python -m scripts.seed_sample_reports
```

you can use:
- email: `demo@example.com`
- password: `demo-password`

## Documentation

- [Install and local setup](docs/INSTALL.md)
- [API reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Vapi setup](docs/VAPI_SETUP.md)
- [Google Calendar setup](docs/GOOGLE_CALENDAR_SETUP.md)
- [Testing](docs/TESTING.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Production hardening notes](docs/PRODUCTION.md)
- [Safety and scope](docs/SAFETY.md)

## Production notes

This repo is a strong production-shaped starter, not a medical device.

Still recommended before real-world rollout:
- lab-specific parser tuning across your report providers
- optional OCR language packs beyond English
- managed PostgreSQL, object storage, backups, and secret rotation
- observability dashboards and alerting
- clinician review of recommendation wording and escalation thresholds
