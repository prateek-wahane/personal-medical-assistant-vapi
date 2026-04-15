# Google Calendar Setup

This project schedules the next blood checkup by creating a Google Calendar event and adding a reminder before the appointment.

## What this integration does

- reads the selected report date
- adds `months_after` months, default `6`
- creates a calendar event
- adds a reminder `reminder_days_before` days before, default `14`

## Step 1. Create a Google Cloud project

In Google Cloud:
- create or select a project
- enable **Google Calendar API**
- configure the OAuth consent screen if required
- create **OAuth client credentials** for a **Desktop app**

## Step 2. Download the credentials file

Save the OAuth JSON file as:

```text
credentials/google_client_secret.json
```

## Step 3. Update `.env`

```env
GOOGLE_CLIENT_SECRETS_FILE=./credentials/google_client_secret.json
GOOGLE_TOKEN_FILE=./credentials/google_token.json
GOOGLE_CALENDAR_ID=primary
```

## Step 4. Authenticate locally

Run:

```bash
python -m scripts.google_calendar_auth
```

This opens a browser window for Google sign-in and stores the token at:

```text
credentials/google_token.json
```

## Step 5. Test scheduling

Use the API docs and call:

`POST /api/reports/schedule-next-checkup`

Example request body:

```json
{
  "report_id": "YOUR_REPORT_ID",
  "months_after": 6,
  "reminder_days_before": 14
}
```

## Event behavior

The event is created against the calendar configured by `GOOGLE_CALENDAR_ID`.

Defaults:
- calendar: `primary`
- follow-up interval: 6 months
- reminder lead time: 14 days

## Production note

For production:
- use a dedicated Google Cloud project
- protect credential files with a secrets manager
- rotate secrets and revoke tokens when needed
- consider using a service account pattern only if your calendar ownership model supports it
