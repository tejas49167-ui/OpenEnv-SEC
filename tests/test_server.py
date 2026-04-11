from fastapi.testclient import TestClient

from env.data import load_examples
from env.models import Action, build_environment_metadata
from server.app import app, benchmark_info, health, list_tasks, root
from server.fallback_app import ResetRequest, create_fallback_app


def test_tasks_endpoint_returns_all_tasks():
    payload = list_tasks()
    assert [task["id"] for task in payload["tasks"]] == ["easy", "medium", "hard"]


def test_benchmark_endpoint_exposes_summary():
    payload = benchmark_info()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "application security" in payload["domain"]
    assert payload["episodes"] == len(load_examples())


def test_root_endpoint_returns_html_landing_page():
    html = root()
    assert "<!DOCTYPE html>" in html
    assert "Cyber Vulnerability Triage" in html
    assert "/docs" in html


def test_root_endpoint_respects_base_path_links():
    html = root("/web")
    assert 'href="/web/docs"' in html
    assert 'href="/web/health"' in html


def test_health_endpoint_reports_healthy_status():
    assert health() == {"status": "healthy"}


def test_http_routes_are_registered():
    routes = {
        (route.path, tuple(sorted(route.methods)))
        for route in app.routes
        if hasattr(route, "methods")
    }
    assert ("/", ("GET",)) in routes
    assert ("/health", ("GET",)) in routes
    assert ("/reset", ("POST",)) in routes
    assert ("/step", ("POST",)) in routes


def test_web_base_path_serves_root_route():
    client = TestClient(app)
    response = client.get("/web")
    assert response.status_code == 200
    assert "Cyber Vulnerability Triage" in response.text


def test_web_base_path_serves_health_route():
    client = TestClient(app)
    response = client.get("/web/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_metadata_endpoint_returns_environment_metadata():
    payload = build_environment_metadata().model_dump()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "description" in payload
    assert payload["dataset_size"] >= 48


def test_fallback_api_reset_and_step_flow():
    fallback_app = create_fallback_app()
    reset_endpoint = next(route.endpoint for route in fallback_app.routes if route.path == "/reset")
    step_endpoint = next(route.endpoint for route in fallback_app.routes if route.path == "/step")

    reset_payload = reset_endpoint(ResetRequest(task="easy"))
    observation = reset_payload["observation"]
    assert observation["task"] == "easy"
    assert reset_payload["done"] is False

    step_payload = step_endpoint(Action(action_type="inspect_payload"))
    assert step_payload["done"] is False
    assert "reward" in step_payload
    assert "observation" in step_payload
