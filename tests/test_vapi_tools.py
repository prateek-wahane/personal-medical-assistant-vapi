from __future__ import annotations

import hashlib
import hmac
import json

from app.config import get_settings


def _sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vapi_tool_requires_user_context_even_with_valid_signature(client, monkeypatch):
    settings = get_settings()
    original = settings.vapi_webhook_secret
    settings.vapi_webhook_secret = "secret123"
    try:
        payload = {"message": {"type": "tool-calls", "toolCallList": [{"id": "1", "name": "get_latest_report_summary", "arguments": {}}]}}
        body = json.dumps(payload).encode("utf-8")
        response = client.post("/api/vapi/tool-calls", content=body, headers={"x-vapi-signature": _sign(body, "secret123"), "Content-Type": "application/json"})
        assert response.status_code == 200
        assert "User context is required" in response.json()["results"][0]["result"]["message"]
    finally:
        settings.vapi_webhook_secret = original


def test_vapi_tool_returns_scoped_summary(client, monkeypatch):
    settings = get_settings()
    original = settings.vapi_webhook_secret
    settings.vapi_webhook_secret = "secret123"
    try:
        client.post("/api/auth/register", json={"email": "voice@example.com", "password": "StrongPass123"})
        login = client.post("/api/auth/login", json={"email": "voice@example.com", "password": "StrongPass123"})
        token = login.json()["access_token"]
        user_id = login.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/api/reports/upload",
            headers=headers,
            files={"file": ("report.txt", b"Hemoglobin 12.1 g/dL 13.0 - 17.0", "text/plain")},
            data={"report_date": "2026-04-15"},
        )

        payload = {
            "message": {
                "type": "tool-calls",
                "metadata": {"userId": user_id},
                "toolCallList": [{"id": "1", "name": "get_latest_report_summary", "arguments": {}}],
            }
        }
        body = json.dumps(payload).encode("utf-8")
        response = client.post(
            "/api/vapi/tool-calls",
            content=body,
            headers={"x-vapi-signature": _sign(body, "secret123"), "Content-Type": "application/json"},
        )
        assert response.status_code == 200
        summary = response.json()["results"][0]["result"]["summary"]
        assert "Parsed 1 markers" in summary
    finally:
        settings.vapi_webhook_secret = original
