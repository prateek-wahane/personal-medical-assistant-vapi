from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vapi_tool_calls_empty_payload():
    response = client.post("/api/vapi/tool-calls", json={"message": {"type": "other"}})
    assert response.status_code == 200
    assert response.json() == {"results": []}
