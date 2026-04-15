# Personal Medical Assistant with Vapi

A production-oriented starter project for a **voice-based personal medical assistant** that can:

- accept blood report uploads
- extract common lab markers from a report
- compare two reports and explain what improved or worsened
- provide **educational** food, supplement, and lifestyle guidance with medical safety guardrails
- schedule the next blood checkup **6 months later**
- create a Google Calendar event with a **14-day reminder**
- expose **Vapi custom tool** and **custom knowledge-base** endpoints

## What you get

- **FastAPI backend** for uploads, parsing, comparison, recommendations, and Vapi webhooks
- **SQLite** for local development
- **Google Calendar API** integration for next-checkup scheduling
- **Vapi tool-calls endpoint** for voice assistant actions
- **Optional Vapi custom knowledge-base endpoint** for report-aware retrieval
- **Simple HTML frontend** for upload, compare, and embedding the Vapi widget
- **Tests** and a **GitHub Actions CI workflow**
- **Docs** for install, Vapi setup, Calendar setup, deployment, testing, and GitHub push

## Repository

- GitHub: `https://github.com/prateek-wahane/personal-medical-assistant-vapi`
- Clone:

```bash
git clone https://github.com/prateek-wahane/personal-medical-assistant-vapi.git
cd personal-medical-assistant-vapi
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open:
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## Documentation

- [Install and local setup](docs/INSTALL.md)
- [Vapi integration setup](docs/VAPI_SETUP.md)
- [Google Calendar setup](docs/GOOGLE_CALENDAR_SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API reference](docs/API.md)
- [Testing](docs/TESTING.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Safety and scope](docs/SAFETY.md)
- [GitHub repo setup and push steps](docs/GITHUB_SETUP.md)

## Repo structure

```text
app/
  main.py
  config.py
  db.py
  models.py
  schemas.py
  routers/
    health.py
    reports.py
    vapi.py
  services/
    pdf_parser.py
    lab_extractor.py
    comparison.py
    recommendations.py
    calendar_service.py
    knowledge_base.py
    vapi_dispatch.py
  prompts/
    assistant_system_prompt.txt

config/vapi/
  tools.json
  assistant.json
  knowledge_base.json

frontend/
  index.html
  app.js

scripts/
  create_vapi_assets.py
  google_calendar_auth.py
  seed_sample_reports.py
  create_github_repo.sh
  create_github_repo.ps1

docs/
  INSTALL.md
  VAPI_SETUP.md
  GOOGLE_CALENDAR_SETUP.md
  API.md
  ARCHITECTURE.md
  TESTING.md
  DEPLOYMENT.md
  SAFETY.md
  GITHUB_SETUP.md
```

## Core flows

### 1. Upload and parse report
- `POST /api/reports/upload`
- Extract text from the uploaded report
- Normalize marker names
- Store report metadata and lab results in the database

### 2. Compare reports
- `POST /api/reports/compare`
- Compare older and newer values
- Return per-marker trend data and a plain-language summary

### 3. Explain a marker
- `GET /api/reports/{report_id}/recommendation/{marker_key}`
- Return educational guidance for that marker
- Include food, lifestyle, and clinician follow-up notes

### 4. Schedule next checkup
- `POST /api/reports/schedule-next-checkup`
- Add the next blood checkup to Google Calendar
- Create a reminder 14 days before by default

### 5. Let Vapi call the backend
- `POST /api/vapi/tool-calls`
- `POST /api/vapi/knowledge-base`

## Local testing flow

1. Start the backend.
2. Seed sample data:

```bash
python -m scripts.seed_sample_reports
```

3. Open Swagger UI at `http://localhost:8000/docs`.
4. Try upload, compare, recommendation, and schedule endpoints.
5. Connect Vapi once your tunnel and credentials are ready.

## Production notes

This repo is a strong MVP starter, not a medical device.

Before production rollout, add:
- authentication and per-user data isolation
- encrypted storage and secret management
- report-format-specific extraction templates
- OCR support for scanned reports
- audit logging and observability
- rate limiting and webhook verification hardening
- a clinical review workflow for wording and recommendation rules
- a real database such as PostgreSQL

## License

This starter includes an MIT license in `LICENSE`.
