from __future__ import annotations

import os
from typing import Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import TASK_LABELS
from env.models import Action


class ResetRequest(BaseModel):
    task: Optional[Literal["easy", "medium", "hard"]] = None


app = FastAPI(title="Cybersecurity Alert Triage OpenEnv", version="2.0.0")
environment = CyberVulnerabilityTriageEnvironment()


@app.get("/")
def root() -> dict:
    return {
        "name": "cyber-vulnerability-triage",
        "status": "ok",
        "tasks": [{"id": task_id, "label": TASK_LABELS[task_id]} for task_id in ["easy", "medium", "hard"]],
        "description": "Multi-step OpenEnv environment for cybersecurity alert triage.",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None) -> dict:
    observation = environment.reset(request.task if request else None)
    return observation.model_dump()


@app.post("/step")
def step(action: Action) -> dict:
    observation, reward, done, info = environment.step(action)
    return {
        "observation": observation.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def state() -> dict:
    return environment.state().model_dump()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
