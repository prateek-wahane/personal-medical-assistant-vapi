# Deployment

## Local Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

## Recommended starter platforms

- Render
- Railway
- Fly.io
- Google Cloud Run
- a small VM with Docker

## Minimum production upgrades

Before real users:
- move SQLite to PostgreSQL
- move uploaded files to object storage
- add authentication
- add encrypted secret handling
- add request logging and monitoring
- add rate limiting
- add OCR for scanned reports
- add background workers for long-running parsing
- add stricter webhook verification and access control

## Example environment setup for production

```env
APP_ENV=prod
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/medical_assistant
UPLOAD_DIR=/app/uploads
PUBLIC_BASE_URL=https://your-domain.example
GOOGLE_CALENDAR_ID=primary
VAPI_WEBHOOK_SECRET=replace_me
```

## Deployment sequence

1. deploy the backend
2. verify `/health`
3. configure environment variables
4. connect Google Calendar credentials securely
5. expose HTTPS domain
6. point Vapi tool server URL to the deployed backend
7. run end-to-end tests

## Observability

Add at minimum:
- application logs
- request IDs
- error tracking
- uptime checks
- database backups
