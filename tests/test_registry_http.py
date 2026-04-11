"""HTTP contract tests for registry-backed FastAPI apps."""

from __future__ import annotations

import asyncio

import pytest

from sec_openenv.framework.registry import get_environment
from sec_openenv.server.factory import ResetRequest, create_environment_app


def _route_endpoint(app, path: str):
    return next(route.endpoint for route in app.routes if route.path == path)


class _MockRequest:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    async def json(self) -> dict:
        return self._payload


@pytest.mark.parametrize("slug", ["cyber-vulnerability-triage", "log-anomaly"])
def test_registry_app_health_benchmark_metadata_tasks(slug: str) -> None:
    app = create_environment_app(slug)

    health = _route_endpoint(app, "/health")()
    assert health == {"status": "healthy"}

    benchmark = _route_endpoint(app, "/benchmark")()
    assert benchmark["name"] == slug
    assert "tasks" in benchmark and len(benchmark["tasks"]) >= 1

    metadata = _route_endpoint(app, "/metadata")()
    assert "name" in metadata

    tasks = _route_endpoint(app, "/tasks")()
    assert "tasks" in tasks and len(tasks["tasks"]) >= 1


@pytest.mark.parametrize(
    ("slug", "task", "step_body"),
    [
        ("cyber-vulnerability-triage", "easy", {"action_type": "inspect_payload"}),
        ("log-anomaly", "screen", {"action_type": "inspect_log"}),
    ],
)
def test_registry_app_reset_step_smoke(slug: str, task: str, step_body: dict) -> None:
    app = create_environment_app(slug)
    reset_endpoint = _route_endpoint(app, "/reset")
    step_endpoint = _route_endpoint(app, "/step")
    action_model = get_environment(slug).load_action_model()

    reset = reset_endpoint(ResetRequest(task=task, seed=0))
    assert "observation" in reset
    assert reset.get("done") is False

    step = asyncio.run(step_endpoint(_MockRequest(step_body)))
    assert "observation" in step
    assert "reward" in step


def test_environment_server_modules_expose_app() -> None:
    from sec_openenv.environments.cyber_vulnerability_triage import server as cyber_server
    from sec_openenv.environments.log_anomaly import server as log_server

    for mod in (cyber_server, log_server):
        assert hasattr(mod, "app")
        assert mod.app.routes


def test_registry_load_server_matches_factory(slug: str = "log-anomaly") -> None:
    descriptor = get_environment(slug)
    loaded = descriptor.load_server()
    assert hasattr(loaded, "routes")
    health_endpoint = _route_endpoint(loaded, "/health")
    assert health_endpoint() == {"status": "healthy"}
