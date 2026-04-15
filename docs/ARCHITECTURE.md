# Architecture

## High-level design

```text
User
  ↓
Vapi Assistant
  ↓
Vapi Tools / KB Requests
  ↓
FastAPI Backend
  ├─ Report parsing
  ├─ Marker extraction
  ├─ Report comparison
  ├─ Recommendation engine
  ├─ Calendar scheduling
  └─ SQLite database
```

## Main components

### FastAPI backend
Responsible for:
- report upload
- text extraction
- marker normalization
- report comparison
- educational recommendation generation
- calendar scheduling
- Vapi tool dispatch

### Database
Local development uses SQLite.

Tables are used for:
- reports
- lab results
- checkup events

### Vapi integration
Vapi does the conversation layer. The backend handles the reliable structured actions.

### Google Calendar
Used to create the follow-up checkup and reminder.

## Why structured comparison matters

Comparing raw PDFs conversationally is unreliable. This project converts reports into structured marker data first, then compares numeric values directly.

## Recommended production evolution

- replace SQLite with PostgreSQL
- store uploaded files in object storage
- move heavy parsing into async jobs
- add OCR pipeline for scanned PDFs
- add auth and user isolation
- add audit logs and observability
