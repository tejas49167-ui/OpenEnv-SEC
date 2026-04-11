from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from env.data import load_examples
from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import Action, build_environment_metadata
from env.tasks import TASKS

try:
    from .landing_page import render_landing_page
except ImportError:
    from server.landing_page import render_landing_page


class ResetRequest(BaseModel):
    task: Literal["easy", "medium", "hard"] | None = None


app = FastAPI(title="Cybersecurity Alert Triage OpenEnv", version="2.1.0")
environment = CyberVulnerabilityTriageEnvironment()


@app.middleware("http")
async def support_hugging_face_base_path(request: Request, call_next):
    if request.scope["path"].startswith("/web"):
        trimmed_path = request.scope["path"][len("/web") :] or "/"
        request.scope["root_path"] = "/web"
        request.scope["path"] = trimmed_path
    return await call_next(request)


def health() -> dict[str, str]:
    return {"status": "healthy"}


def root(base_path: str = "") -> str:
    return render_landing_page(base_path=base_path)


def metadata() -> dict:
    return build_environment_metadata().model_dump()


def list_tasks() -> dict[str, list[dict[str, object]]]:
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


def benchmark_info() -> dict[str, object]:
    return {
        "name": "cyber-vulnerability-triage",
        "domain": "application security incident triage",
        "episodes": len(load_examples()),
        "tasks": list(TASKS.keys()),
    }


@app.get("/health")
def health_route() -> dict[str, str]:
    return health()


@app.get("/", response_class=HTMLResponse)
def root_route(request: Request) -> str:
    return root(base_path=request.scope.get("root_path", ""))


@app.get("/metadata")
def metadata_route() -> dict:
    return metadata()


@app.get("/tasks")
def tasks_route() -> dict[str, list[dict[str, object]]]:
    return list_tasks()


@app.get("/benchmark")
def benchmark_route() -> dict[str, object]:
    return benchmark_info()


@app.post("/reset")
def reset(request: ResetRequest | None = None) -> dict[str, object]:
    observation = environment.reset(task=request.task if request else None)
    return {
        "observation": observation.model_dump(),
        "reward": observation.reward,
        "done": observation.done,
    }


@app.post("/step")
def step(action: Action) -> dict[str, object]:
    observation = environment.step(action)
    return {
        "observation": observation.model_dump(),
        "reward": observation.reward,
        "done": observation.done,
        "info": observation.metadata.get("info", {}),
    }


@app.get("/state")
def state() -> dict:
    return environment.state.model_dump()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
