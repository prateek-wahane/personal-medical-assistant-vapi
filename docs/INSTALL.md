# Install and Local Setup

## Prerequisites

- Python 3.11 or newer
- pip
- Vapi account
- Google Cloud project with Calendar API enabled
- OAuth Desktop credentials for Google Calendar

## 1. Create a virtual environment

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Create environment file

```bash
cp .env.example .env
```

## 4. Run migrations

```bash
alembic upgrade head
```

## 5. Run the API locally

```bash
uvicorn app.main:app --reload
```

Open:
- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## 6. Create a user and login

- `POST /api/auth/register`
- `POST /api/auth/login`

Use the returned bearer token for all `/api/reports/*` endpoints.

## 7. Seed sample reports

```bash
python -m scripts.seed_sample_reports
```

Demo credentials:
- email: `demo@example.com`
- password: `demo-password`

## 8. Upload a real report

Use either:
- Swagger UI at `http://localhost:8000/docs`
- your own frontend
- the included `frontend/index.html`

Endpoint:
- `POST /api/reports/upload`

Form fields:
- `file`
- `report_date`

## 9. Important parser note

This hardened starter safely handles common text-based PDFs better than the original version, including labels like `Vitamin B12` and `25-OH Vitamin D`.

If your lab sends scanned-image PDFs, add OCR before expecting high extraction accuracy.
