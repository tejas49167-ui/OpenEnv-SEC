from fastapi.testclient import TestClient

from server.app import app


def test_tasks_endpoint_returns_all_tasks():
    client = TestClient(app)
    response = client.get("/tasks")
    assert response.status_code == 200
    payload = response.json()
    assert [task["id"] for task in payload["tasks"]] == ["easy", "medium", "hard"]


def test_benchmark_endpoint_exposes_summary():
    client = TestClient(app)
    response = client.get("/benchmark")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "application security" in payload["domain"]


def test_metadata_endpoint_returns_environment_metadata():
    client = TestClient(app)
    response = client.get("/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "description" in payload
