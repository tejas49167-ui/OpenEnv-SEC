from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from sec_openenv.__about__ import __version__
from sec_openenv.core.base import FrameworkMetadata

TaskName = Literal["screen", "investigate", "respond"]
Label = Literal["benign", "bruteforce", "data_exfiltration", "privilege_escalation"]
Severity = Literal["none", "low", "medium", "high"]
ResponseAction = Literal["ignore", "monitor", "isolate_host", "page_oncall"]
ActionType = Literal["inspect_log", "inspect_context", "review_baseline", "submit_triage"]


class LogExample(BaseModel):
    event_id: str
    service: str
    raw_log: str
    label: Label
    severity: Severity
    recommended_action: ResponseAction
    artifacts: dict[str, str]
    useful_actions: list[str] = Field(default_factory=list)


class Action(BaseModel):
    action_type: ActionType
    label: Label | None = None
    severity: Severity | None = None
    response_action: ResponseAction | None = None
    explanation: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_submit(self) -> Action:
        if self.action_type == "submit_triage":
            missing = [
                field
                for field, value in {
                    "label": self.label,
                    "severity": self.severity,
                    "response_action": self.response_action,
                }.items()
                if value is None
            ]
            if missing:
                raise ValueError(f"submit_triage requires fields: {', '.join(missing)}")
        return self


class Reward(BaseModel):
    score: float
    feedback: str


class Observation(BaseModel):
    task: TaskName
    event_id: str
    service: str
    raw_log: str
    instructions: str
    steps_taken: int
    remaining_steps: int
    available_action_types: list[ActionType]
    collected_artifacts: list[str]
    evidence_log: list[str]
    done: bool = False
    reward: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnvironmentState(BaseModel):
    episode_id: str | None = None
    step_count: int = 0
    current_task: TaskName = "screen"
    current_index: int = 0
    steps_taken: int = 0
    max_steps: int = 0
    completed: bool = False
    revealed_artifacts: list[str] = Field(default_factory=list)


def build_environment_metadata(dataset_size: int) -> FrameworkMetadata:
    return FrameworkMetadata(
        name="log-anomaly",
        description="Operational log triage environment for anomaly investigation and response recommendation.",
        domain="detection engineering",
        version=__version__,
        dataset_size=dataset_size,
        documentation_url="https://github.com/tejas/sec-openenv",
        tags=["logs", "anomaly", "response"],
        maturity="alpha",
    )
