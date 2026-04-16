# Install and Local Setup

## 1. Clone the repo

```bash
git clone https://github.com/prateek-wahane/personal-medical-assistant-vapi.git
cd personal-medical-assistant-vapi
```

## 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
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
- `http://localhost:8000/ready`

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
- the frontend demo in `frontend/index.html`

## 9. OCR note

This production pass can attempt OCR fallback on PDFs when native extraction returns too little text. OCR is controlled by `.env` settings and requires the OCR runtime in the container or local machine.
