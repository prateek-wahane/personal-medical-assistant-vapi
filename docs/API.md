# API Reference

## Health

### `GET /health`
Returns a simple health response.

Response:

```json
{
  "status": "ok"
}
```

## Reports

### `POST /api/reports/upload`
Upload a blood report file and parse markers.

Form fields:
- `file`
- `report_date`

### `GET /api/reports`
List all reports ordered by most recent report date.

### `GET /api/reports/{report_id}`
Fetch a single report with parsed results.

### `POST /api/reports/compare`
Compare two reports.

Request body:

```json
{
  "report_id_a": "OLDER_REPORT_ID",
  "report_id_b": "NEWER_REPORT_ID"
}
```

### `GET /api/reports/{report_id}/recommendation/{marker_key}`
Return educational guidance for a marker from a report.

Examples of `marker_key`:
- `hemoglobin`
- `ferritin`
- `vitamin_b12`
- `vitamin_d_25_oh`
- `fasting_glucose`
- `hba1c`
- `ldl`
- `triglycerides`

### `POST /api/reports/schedule-next-checkup`
Create the next blood-check calendar event.

Request body:

```json
{
  "report_id": "REPORT_ID",
  "months_after": 6,
  "reminder_days_before": 14
}
```

## Vapi

### `POST /api/vapi/tool-calls`
Receives Vapi function tool calls and dispatches them to backend services.

### `POST /api/vapi/knowledge-base`
Receives a custom Vapi knowledge-base request and returns relevant report-aware documents.

## Swagger UI

Run the server and open:

```text
http://localhost:8000/docs
```
