# Personal Medical Assistant with Vapi

A production-oriented starter project for a **voice-based personal medical assistant** that can:

- accept blood report uploads
- extract common lab markers from a report
- compare two reports and explain what improved or worsened
- provide **educational** food, supplement, and lifestyle guidance with medical safety guardrails
- schedule the next blood checkup **6 months later**
- create a Google Calendar event with a **14-day reminder**
- expose **Vapi custom tool** and **custom knowledge-base** endpoints
- isolate each user’s reports with login-based access control

## What changed in this hardened version

- added **JWT auth** and per-user report ownership
- added **Alembic migrations** instead of runtime `create_all`
- hardened uploads with file-type, size, and filename protections
- fixed parser bugs for labels containing numbers such as **Vitamin B12** and **25-OH Vitamin D**
- improved comparison safety for **unit mismatches** and reference-range changes
- updated Vapi signature handling to support the documented `sha256=...` header format
- updated the frontend to the current Vapi web widget embed pattern

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Open:
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Frontend: open `frontend/index.html`

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
- [Vapi integration setup](docs/VAPI_SETUP.md)
- [Google Calendar setup](docs/GOOGLE_CALENDAR_SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API reference](docs/API.md)
- [Testing](docs/TESTING.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Safety and scope](docs/SAFETY.md)

## Production notes

This repo is a strong MVP starter, not a medical device.

Still recommended before real-world rollout:
- lab-specific parser tuning across your report providers
- optional OCR pipeline for scanned-image PDFs
- secret management in your deployment platform
- observability, backups, and incident handling
- clinician review of recommendation wording and escalation thresholds
