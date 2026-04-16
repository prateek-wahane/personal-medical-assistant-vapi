# API Reference

## Health

### `GET /health`
Returns application liveness.

### `GET /ready`
Checks application readiness including a database probe.

## Auth

### `POST /api/auth/register`
Create a new user.

### `POST /api/auth/login`
Login and receive a bearer token.

### `GET /api/auth/me`
Return the current authenticated user.

## Reports

All report endpoints require `Authorization: Bearer <token>`.

### `POST /api/reports/upload`
Upload a blood report file and parse markers.

### `GET /api/reports`
List the current user’s reports.

### `GET /api/reports/{report_id}`
Fetch one report owned by the current user.

### `POST /api/reports/compare`
Compare two reports owned by the current user.

### `GET /api/reports/{report_id}/recommendation/{marker_key}`
Return educational guidance for one marker from one report.

### `POST /api/reports/schedule-next-checkup`
Create the next blood-check calendar event.

## Vapi

### `POST /api/vapi/tool-calls`
Receives Vapi function tool calls and dispatches them to backend services.

### `POST /api/vapi/knowledge-base`
Receives a custom Vapi knowledge-base request and returns relevant report-aware documents.
