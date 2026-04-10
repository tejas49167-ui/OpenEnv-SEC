from __future__ import annotations

import os

import uvicorn
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

try:
    from openenv.core.env_server.http_server import create_app
except ImportError:  # pragma: no cover
    from server.fallback_app import create_fallback_app

    app = create_fallback_app()
else:
    try:
        from models import Action, Observation
    except ImportError:
        from ..models import Action, Observation

    try:
        from .cyber_vulnerability_triage_environment import CyberVulnerabilityTriageEnvironment
    except ImportError:
        from server.cyber_vulnerability_triage_environment import CyberVulnerabilityTriageEnvironment

    app = create_app(
        CyberVulnerabilityTriageEnvironment,
        Action,
        Observation,
        env_name="cyber-vulnerability-triage",
        max_concurrent_envs=1,
    )

from env.tasks import TASKS
from server.landing_page import render_landing_page

router = APIRouter(tags=["benchmark"])


@router.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@router.get("/", response_class=HTMLResponse)
def root() -> str:
    return render_landing_page()


@router.get("/tasks")
def list_tasks() -> dict:
    return {
        "tasks": [
            {
                "id": task.name,
                "description": task.description,
                "instructions": task.instructions,
                "max_steps": task.max_steps,
                "required_artifacts_for_full_credit": task.required_artifacts_for_full_credit,
            }
            for task in TASKS.values()
        ]
    }


@router.get("/benchmark")
def benchmark_info() -> dict:
    return {
        "name": "cyber-vulnerability-triage",
        "domain": "application security incident triage",
        "episodes": 12,
        "tasks": list(TASKS.keys()),
        "supports_concurrent_sessions": True,
        "primary_entrypoint": "server.app:app",
    }


app.include_router(router)


def main() -> None:
    port = int(os.getenv("API_PORT", os.getenv("PORT", "8000")))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
