# Testing

## Run the test suite

```bash
pytest
```

## What is covered

The included tests cover:
- report comparison behavior
- recommendation logic
- Vapi tool call behavior

## Manual test checklist

### Upload flow
- start the API
- upload one report
- confirm markers were parsed
- inspect `GET /api/reports`

### Comparison flow
- upload or seed two reports
- call `POST /api/reports/compare`
- verify improved and worsened markers look correct

### Recommendation flow
- request a recommendation for hemoglobin or ferritin
- confirm response stays educational and cautious

### Calendar flow
- authenticate Google Calendar
- schedule the next checkup
- confirm the event appears in your calendar

### Vapi flow
- expose your API with a tunnel
- create or bootstrap Vapi assets
- start a voice session
- ask the assistant to summarize, compare, and schedule

## Parser validation tip

Use 5 to 10 real reports from the same lab first. Tune aliases in `app/services/lab_extractor.py` before testing across multiple lab providers.
