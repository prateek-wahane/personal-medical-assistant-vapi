# Vapi Setup

This project uses Vapi as the conversation layer and your backend as the source of truth for lab comparison and scheduling logic.

## Vapi flow used in this repo

- Vapi assistant handles the conversation
- Vapi custom function tools call your backend
- Your backend returns structured results
- Optional: a custom Vapi knowledge base endpoint lets the assistant retrieve report-aware context

## Backend endpoints used by Vapi

- `POST /api/vapi/tool-calls`
- `POST /api/vapi/knowledge-base`

## Step 1. Expose your local API

For local testing, expose port 8000 with a tunnel.

Example with ngrok:

```bash
ngrok http 8000
```

Set the public URL in `.env`:

```env
PUBLIC_BASE_URL=https://your-subdomain.ngrok-free.app
```

## Step 2. Set Vapi credentials

Update `.env`:

```env
VAPI_API_KEY=your_vapi_private_api_key
VAPI_PUBLIC_KEY=your_vapi_public_key
VAPI_WEBHOOK_SECRET=your_random_secret_for_signature_validation
```

## Step 3. Create tools

This repo includes ready-made tool definitions in:

- `config/vapi/tools.json`

Tool names:
- `get_latest_report_summary`
- `compare_reports`
- `get_marker_recommendation`
- `schedule_next_checkup`

### Option A: Create tools manually in Vapi Dashboard

For each function tool:
- set the tool type to function
- point server URL to:

```text
https://YOUR_BACKEND_DOMAIN/api/vapi/tool-calls
```

- reuse the matching schema from `config/vapi/tools.json`

### Option B: Bootstrap tools and assistant with the script

```bash
python -m scripts.create_vapi_assets
```

This script reads:
- `config/vapi/tools.json`
- `config/vapi/assistant.json`
- `app/prompts/assistant_system_prompt.txt`

It then creates:
- the Vapi tools
- the optional custom knowledge base
- the assistant

Output is saved to:

```text
config/vapi/bootstrap_output.json
```

## Step 4. Create or update the assistant

The assistant base config lives in:
- `config/vapi/assistant.json`

The system prompt lives in:
- `app/prompts/assistant_system_prompt.txt`

Adjust these before running the bootstrap script if you want a different voice, first message, or model.

## Step 5. Attach the web widget

The included frontend has a simple hook point for the Vapi widget.

You will need:
- `VAPI_PUBLIC_KEY`
- `VAPI_ASSISTANT_ID`

Typical flow:
1. upload a report
2. compare reports if two are available
3. start the Vapi conversation
4. let the assistant call tools against the backend

## Suggested first conversation

Ask:
- “Summarize my latest blood report.”
- “Compare my latest report with the previous one.”
- “What should I focus on for hemoglobin?”
- “Schedule my next blood test in six months.”

## Vapi implementation note

Keep medical reasoning in the backend. Use Vapi for the conversation and tool orchestration, not as the sole source of lab comparison truth.
