from __future__ import annotations

from io import BytesIO


def test_register_login_and_upload_are_scoped(client):
    first = client.post("/api/auth/register", json={"email": "first@example.com", "password": "StrongPass123"})
    second = client.post("/api/auth/register", json={"email": "second@example.com", "password": "StrongPass123"})
    assert first.status_code == 201
    assert second.status_code == 201

    login_one = client.post("/api/auth/login", json={"email": "first@example.com", "password": "StrongPass123"})
    login_two = client.post("/api/auth/login", json={"email": "second@example.com", "password": "StrongPass123"})
    headers_one = {"Authorization": f"Bearer {login_one.json()['access_token']}"}
    headers_two = {"Authorization": f"Bearer {login_two.json()['access_token']}"}

    upload_response = client.post(
        "/api/reports/upload",
        headers=headers_one,
        files={"file": ("report.txt", b"Hemoglobin 12.1 g/dL 13.0 - 17.0", "text/plain")},
        data={"report_date": "2026-04-15"},
    )
    assert upload_response.status_code == 201

    list_one = client.get("/api/reports", headers=headers_one)
    list_two = client.get("/api/reports", headers=headers_two)
    assert len(list_one.json()) == 1
    assert list_two.json() == []


def test_upload_rejects_unsupported_extension(client, auth_headers):
    response = client.post(
        "/api/reports/upload",
        headers=auth_headers,
        files={"file": ("report.exe", b"not allowed", "application/octet-stream")},
        data={"report_date": "2026-04-15"},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
