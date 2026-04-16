# Deployment

## Local Docker

```bash
docker compose up --build
```

The container runs:
- `alembic upgrade head`
- `uvicorn app.main:app`

## Environment variables to set in production

```env
APP_ENV=prod
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/medical_assistant
AUTH_SECRET_KEY=replace-this-with-a-long-random-secret
CORS_ALLOWED_ORIGINS=https://your-frontend.example
PUBLIC_BASE_URL=https://your-api.example
GOOGLE_CALENDAR_ID=primary
VAPI_WEBHOOK_SECRET=replace-me
```

## Minimum production upgrades still recommended

- PostgreSQL instead of SQLite
- object storage for report files
- OCR pipeline for scanned PDFs
- rate limiting and structured logging
- secrets manager for OAuth and API secrets
- clinician-reviewed recommendation policies
