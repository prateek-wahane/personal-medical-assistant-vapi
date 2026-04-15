import hmac
from hashlib import sha256

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.services.knowledge_base import search_reports
from app.services.vapi_dispatch import handle_tool_call

router = APIRouter(prefix="/api/vapi", tags=["vapi"])


def _verify_secret(body: bytes, provided_signature: str | None):
    settings = get_settings()
    if not settings.vapi_webhook_secret:
        return

    if not provided_signature:
        raise HTTPException(status_code=401, detail="Missing Vapi signature header")

    digest = hmac.new(
        settings.vapi_webhook_secret.encode("utf-8"),
        body,
        sha256,
    ).hexdigest()

    if not hmac.compare_digest(digest, provided_signature):
        raise HTTPException(status_code=401, detail="Invalid Vapi signature")


@router.post("/tool-calls")
async def tool_calls(
    request: Request,
    db: Session = Depends(get_db),
    x_vapi_signature: str | None = Header(default=None),
):
    body = await request.body()
    _verify_secret(body, x_vapi_signature)

    payload = await request.json()
    message = payload.get("message", {})
    if message.get("type") != "tool-calls":
        return {"results": []}

    results = []
    for tool_call in message.get("toolCallList", []):
        result = handle_tool_call(db, tool_call.get("name", ""), tool_call.get("arguments", {}) or {})
        results.append(
            {
                "toolCallId": tool_call.get("id"),
                "result": result,
            }
        )
    return {"results": results}


@router.post("/knowledge-base")
async def knowledge_base(
    request: Request,
    db: Session = Depends(get_db),
    x_vapi_signature: str | None = Header(default=None),
):
    body = await request.body()
    _verify_secret(body, x_vapi_signature)

    payload = await request.json()
    message = payload.get("message", {})
    if message.get("type") != "knowledge-base-request":
        return {"documents": []}

    messages = message.get("messages", [])
    latest_user_message = ""
    for item in reversed(messages):
        if item.get("role") == "user":
            latest_user_message = item.get("content", "")
            break

    documents = search_reports(db, latest_user_message)
    return {"documents": documents}
