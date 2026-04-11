from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
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
    seed: int | None = None
    case_index: int | None = None


def create_fallback_app() -> FastAPI:
    app = FastAPI(title="Cybersecurity Alert Triage OpenEnv", version="2.1.0")
    environment = CyberVulnerabilityTriageEnvironment()

    @app.get("/health")
    def health() -> dict:
        return {"status": "healthy"}

    @app.get("/", response_class=HTMLResponse)
    def root() -> str:
        return render_landing_page()

    @app.get("/metadata")
    def metadata() -> dict:
        return build_environment_metadata().model_dump()

    @app.post("/reset")
    def reset(request: ResetRequest | None = None) -> dict:
        observation = environment.reset(
            task=request.task if request else None,
            seed=request.seed if request else None,
            case_index=request.case_index if request else None,
        )
        return {
            "observation": observation.model_dump(),
            "reward": observation.reward,
            "done": observation.done,
        }

    @app.post("/step")
    def step(action: Action) -> dict:
        try:
            observation = environment.step(action)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "observation": observation.model_dump(),
            "reward": observation.reward,
            "done": observation.done,
            "info": observation.metadata.get("info", {}),
        }

    @app.get("/state")
    def state() -> dict:
        return environment.state.model_dump()

    @app.get("/tasks")
    def tasks() -> dict:
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

    @app.get("/benchmark")
    def benchmark() -> dict:
        return {
            "name": "cyber-vulnerability-triage",
            "domain": "application security incident triage",
            "episodes": len(load_examples()),
            "tasks": list(TASKS.keys()),
        }

    return app
