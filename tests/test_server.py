from server.app import benchmark_info, list_tasks
from env.models import build_environment_metadata


def test_tasks_endpoint_returns_all_tasks():
    payload = list_tasks()
    assert [task["id"] for task in payload["tasks"]] == ["easy", "medium", "hard"]


def test_benchmark_endpoint_exposes_summary():
    payload = benchmark_info()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "application security" in payload["domain"]


def test_metadata_endpoint_returns_environment_metadata():
    payload = build_environment_metadata().model_dump()
    assert payload["name"] == "cyber-vulnerability-triage"
    assert "description" in payload
