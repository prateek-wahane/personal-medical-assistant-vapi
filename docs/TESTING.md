# Testing

Run the test suite:

```bash
pytest
```

## What is covered

- auth hashing and login flow
- parser behavior for numeric labels like Vitamin B12 and 25-OH Vitamin D
- upload safety behavior
- comparison logic including unit mismatches
- Vapi signature handling and scoped tool behavior
- OCR fallback path at the parser layer
- readiness and request-id behavior

## CI

CI now boots PostgreSQL, runs `alembic upgrade head`, and then runs the tests.
