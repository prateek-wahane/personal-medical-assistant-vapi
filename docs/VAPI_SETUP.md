# Vapi Setup

This project uses Vapi as the conversation layer and your backend as the source of truth for comparison, guidance, scheduling, and user isolation.

## Backend endpoints used by Vapi

- `POST /api/vapi/tool-calls`
- `POST /api/vapi/knowledge-base`

## Signature handling

This backend accepts the documented Vapi webhook signature format:
- `x-vapi-signature: sha256=<hex-digest>`

## User isolation in voice mode

To make the assistant operate only on the current logged-in user’s reports, pass `userId` in assistant metadata or variable values when starting the widget or call.

The included frontend does this automatically after login using `assistant-overrides`.

## Local widget

The frontend now uses the current Vapi embed widget pattern with:
- `https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js`
- `<vapi-widget ...></vapi-widget>`
