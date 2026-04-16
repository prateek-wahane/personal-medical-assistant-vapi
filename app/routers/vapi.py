from __future__ import annotations

import hmac
from hashlib import sha256
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.services.knowledge_base import search_reports
from app.services.vapi_dispatch import handle_tool_call

router = APIRouter(prefix="/api/vapi", tags=["vapi"])



def _verify_secret(body: bytes, provided_signature: str | None):
    settings = get_settings()
    resolved_secret = settings.resolved_vapi_webhook_secret
    if not resolved_secret:
        return

    if not provided_signature:
        raise HTTPException(status_code=401, detail="Missing Vapi signature header")

    digest = hmac.new(resolved_secret.encode("utf-8"), body, sha256).hexdigest()
    expected_variants = {digest, f"sha256={digest}"}
    if provided_signature.strip() not in expected_variants:
        raise HTTPException(status_code=401, detail="Invalid Vapi signature")



def _extract_user_id(payload: dict[str, Any], tool_args: dict[str, Any] | None = None) -> str | None:
    tool_args = tool_args or {}
    message = payload.get("message", {}) or {}
    call = message.get("call", {}) or {}
    candidate_paths = [
        tool_args.get("user_id"),
        payload.get("userId"),
        payload.get("user_id"),
        (payload.get("metadata") or {}).get("userId"),
        (payload.get("metadata") or {}).get("user_id"),
        message.get("userId"),
        message.get("user_id"),
        (message.get("metadata") or {}).get("userId"),
        (message.get("metadata") or {}).get("user_id"),
        (call.get("metadata") or {}).get("userId"),
        (call.get("metadata") or {}).get("user_id"),
        ((call.get("assistantOverrides") or {}).get("variableValues") or {}).get("userId"),
        ((call.get("assistantOverrides") or {}).get("variableValues") or {}).get("user_id"),
    ]
    for value in candidate_paths:
        if value:
            return str(value)
    return None


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
        arguments = tool_call.get("arguments", {}) or {}
        user_id = _extract_user_id(payload, arguments)
        result = handle_tool_call(db, tool_call.get("name", ""), arguments, user_id=user_id)
        results.append({"toolCallId": tool_call.get("id"), "result": result})
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

    user_id = _extract_user_id(payload)
    if not user_id:
        return {"documents": []}
    documents = search_reports(db, latest_user_message, user_id=user_id)
    return {"documents": documents}
