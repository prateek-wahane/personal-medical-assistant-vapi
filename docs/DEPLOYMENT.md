# Deployment

## Local production-like run

```bash
docker compose -f docker-compose.prod.yml up --build
```

This stack includes PostgreSQL 16 and the API service.

## Cloud Run deployment shape

Use:
- `cloudrun/service.yaml` for the web service
- `cloudrun/ocr-job.yaml` for OCR backfill or batch processing

## Environment variables to set in production

```env
APP_ENV=prod
JSON_LOGS=true
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/medical_assistant
CORS_ALLOWED_ORIGINS=https://your-frontend.example
PUBLIC_BASE_URL=https://your-api.example
OCR_ENABLED=true
AUTH_SECRET_KEY_FILE=/secrets/auth-secret
VAPI_WEBHOOK_SECRET_FILE=/secrets/vapi-webhook-secret
GOOGLE_CLIENT_SECRETS_FILE=/secrets/google-client-secret.json
GOOGLE_TOKEN_FILE=/secrets/google-token.json
```

## Secrets

Prefer mounted secret files in production over inline environment variables.

The app supports:
- `AUTH_SECRET_KEY_FILE`
- `VAPI_WEBHOOK_SECRET_FILE`

## Minimum production upgrades still recommended

- managed PostgreSQL instead of container-local Postgres
- object storage for report files
- OCR language packs based on your user base
- rate-limit state backed by Redis instead of in-memory storage
- structured logging sink, error tracking, and metrics dashboards
- clinician-reviewed recommendation policies
