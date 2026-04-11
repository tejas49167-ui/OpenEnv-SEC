from fastapi.testclient import TestClient

from server.app import app, benchmark_info, health, list_tasks, root
from env.models import build_environment_metadata


def test_tasks_endpoint_returns_all_tasks():
    payload = list_tasks()
    assert [task["id"] for task in payload["tasks"]] == ["easy", "medium", "hard"]


def test_benchmark_endpoint_exposes_summary():
    payload = benchmark_info()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "application security" in payload["domain"]


def test_root_endpoint_returns_html_landing_page():
    html = root()
    assert "<!DOCTYPE html>" in html
    assert "Cyber Vulnerability Triage" in html
    assert "/docs" in html


def test_health_endpoint_reports_healthy_status():
    assert health() == {"status": "healthy"}


def test_http_routes_return_expected_content_types():
    client = TestClient(app)
    root_response = client.get("/")
    health_response = client.get("/health")
    assert root_response.status_code == 200
    assert root_response.headers["content-type"].startswith("text/html")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "healthy"}


def test_metadata_endpoint_returns_environment_metadata():
    payload = build_environment_metadata().model_dump()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "description" in payload
