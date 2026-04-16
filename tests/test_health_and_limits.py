from __future__ import annotations


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_request_id_header_present(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
