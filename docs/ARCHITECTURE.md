# Architecture

## High-level design

```text
User
  ↓
JWT Auth Layer
  ↓
FastAPI Backend
  ├─ report upload and safe file storage
  ├─ parser and lab normalization
  ├─ comparison engine
  ├─ educational recommendation engine
  ├─ Google Calendar scheduling
  ├─ Vapi tool and knowledge-base endpoints
  └─ database via Alembic-managed schema
```

## Main hardening changes

- each report belongs to a `user_id`
- report queries are scoped to the authenticated user
- Vapi requests can also scope to a user via metadata or variable values
- uploads are stored with generated filenames instead of user-supplied paths
- migrations replace runtime schema creation
