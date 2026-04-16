# Architecture

```text
User
  ↓
JWT Auth Layer
  ↓
FastAPI Backend
  ├─ safe report upload and storage metadata
  ├─ native PDF extraction
  ├─ OCR fallback for scanned PDFs
  ├─ parser and lab normalization
  ├─ comparison engine
  ├─ educational recommendation engine
  ├─ Google Calendar scheduling
  ├─ Vapi tool and knowledge-base endpoints
  └─ PostgreSQL/SQLite via Alembic-managed schema
```

## Main hardening changes

- each report belongs to a `user_id`
- report queries are scoped to the authenticated user
- Vapi requests can also scope to a user via metadata or variable values
- uploads are stored with generated filenames instead of user-supplied paths
- OCR is attempted when native PDF text extraction is too weak
- request IDs and basic rate limits are applied at middleware level
