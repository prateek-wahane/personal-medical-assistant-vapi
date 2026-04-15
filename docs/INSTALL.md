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

Windows PowerShell:

```powershell
copy .env.example .env
```

## 4. Review `.env`

Minimum values to review:

```env
APP_NAME=Personal Medical Assistant
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=sqlite:///./medical_assistant.db
UPLOAD_DIR=./uploads
TIMEZONE=Asia/Kolkata
GOOGLE_CLIENT_SECRETS_FILE=./credentials/google_client_secret.json
GOOGLE_TOKEN_FILE=./credentials/google_token.json
GOOGLE_CALENDAR_ID=primary
VAPI_API_KEY=
VAPI_PUBLIC_KEY=
VAPI_ASSISTANT_ID=
VAPI_WEBHOOK_SECRET=
PUBLIC_BASE_URL=http://localhost:8000
```

## 5. Run the API locally

```bash
uvicorn app.main:app --reload
```

Open:
- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## 6. Seed sample reports

```bash
python -m scripts.seed_sample_reports
```

This helps you test compare and recommendation flows before using real blood reports.

## 7. Upload a real report

Use either:
- Swagger UI at `http://localhost:8000/docs`
- your own frontend
- the included `frontend/index.html`

Endpoint:
- `POST /api/reports/upload`

Form fields:
- `file`
- `report_date`

## 8. Important parser note

This starter works best on text-based PDFs or text reports. If your lab sends scanned-image PDFs, add OCR support before expecting high extraction accuracy.
