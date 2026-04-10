from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

try:
    from openenv.core.env_server.types import (
        Action as OpenEnvAction,
        EnvironmentMetadata,
        Observation as OpenEnvObservation,
        State as OpenEnvState,
    )
except ImportError:  # pragma: no cover
    class OpenEnvAction(BaseModel):
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class OpenEnvObservation(BaseModel):
        done: bool = False
        reward: Optional[float] = None
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class OpenEnvState(BaseModel):
        episode_id: Optional[str] = None
        step_count: int = 0

    class EnvironmentMetadata(BaseModel):
        name: str
        description: str
        readme_content: Optional[str] = None
        version: Optional[str] = None
        author: Optional[str] = None
        documentation_url: Optional[str] = None

VulnerabilityType = Literal[
    "safe",
    "xss",
    "sql_injection",
    "command_injection",
    "path_traversal",
]
SeverityLevel = Literal["none", "low", "medium", "high", "critical"]
ResponseAction = Literal["allow", "block", "sanitize", "monitor"]
TaskName = Literal["easy", "medium", "hard"]
ActionType = Literal[
    "inspect_payload",
    "decode_obfuscation",
    "review_history",
    "check_source_reputation",
    "inspect_asset_context",
    "consult_playbook",
    "submit_triage",
]
ArtifactName = Literal[
    "payload_analysis",
    "decoded_input",
    "traffic_history",
    "source_reputation",
    "asset_context",
    "playbook_guidance",
]

TASK_LABELS: Dict[TaskName, str] = {
    "easy": "Easy (Quick classification)",
    "medium": "Medium (Severity + evidence)",
    "hard": "Hard (Full triage workflow)",
}


class RequestExample(BaseModel):
    request_id: str
    queue: str
    title: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: str = ""
    source_ip: str
    user_agent: str
    vulnerability_type: VulnerabilityType
    severity: SeverityLevel
    recommended_action: ResponseAction
    explanation_keywords: List[str] = Field(default_factory=list)
    analyst_notes: str
    service: Optional[str] = None
    deployment_tier: Optional[str] = None
    business_impact: Optional[str] = None
    detection_source: Optional[str] = None
    customer_impact: Optional[str] = None
    analyst_handoff: Optional[str] = None
    artifacts: Dict[ArtifactName, str]
    useful_actions: List[ActionType] = Field(default_factory=list)


class Observation(OpenEnvObservation):
    task: TaskName
    task_label: str
    request_id: str
    queue: str
    title: str
    service: str
    deployment_tier: str
    triage_priority: str
    business_impact: str
    detection_source: str
    customer_impact: str
    analyst_handoff: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: str
    source_ip: str
    user_agent: str
    instructions: str
    steps_taken: int
    remaining_steps: int
    available_artifacts: List[ArtifactName]
    collected_artifacts: List[ArtifactName]
    evidence_log: List[str]
    available_action_types: List[ActionType]
    allowed_vulnerabilities: List[VulnerabilityType]
    allowed_severities: List[SeverityLevel]
    allowed_actions: List[ResponseAction]


class Action(OpenEnvAction):
    action_type: ActionType
    vulnerability_type: Optional[VulnerabilityType] = None
    severity: Optional[SeverityLevel] = None
    response_action: Optional[ResponseAction] = None
    explanation: str = ""

    @model_validator(mode="after")
    def validate_submit_fields(self) -> "Action":
        if self.action_type == "submit_triage":
            required = {
                "vulnerability_type": self.vulnerability_type,
                "severity": self.severity,
                "response_action": self.response_action,
            }
            missing = [name for name, value in required.items() if value is None]
            if missing:
                raise ValueError(f"submit_triage requires fields: {', '.join(missing)}")
        return self


class Reward(BaseModel):
    score: float
    step_score: float = 0.0
    terminal_score: float = 0.0
    investigation_score: float = 0.0
    decision_score: float = 0.0
    efficiency_score: float = 0.0
    safety_penalty: float = 0.0
    feedback: str


class StepInfo(BaseModel):
    task: TaskName
    task_label: str
    request_id: str
    grader_name: str
    steps_taken: int
    revealed_artifacts: List[ArtifactName]
    ground_truth_vulnerability: VulnerabilityType
    ground_truth_severity: SeverityLevel
    ground_truth_action: ResponseAction
    component_scores: Dict[str, float]


class EnvironmentState(OpenEnvState):
    current_task: TaskName = "easy"
    current_index: int = 0
    episode_count: int = 0
    steps_taken: int = 0
    max_steps: int = 0
    completed: bool = False
    last_request_id: Optional[str] = None
    revealed_artifacts: List[ArtifactName] = Field(default_factory=list)
    evidence_log: List[str] = Field(default_factory=list)
    last_reward: Optional[Reward] = None


def build_environment_metadata() -> EnvironmentMetadata:
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else None
    return EnvironmentMetadata(
        name="cyber-vulnerability-triage",
        description=(
            "Multi-step OpenEnv environment for cybersecurity alert triage over "
            "suspicious HTTP requests."
        ),
        readme_content=readme_content,
        version="2.1.0",
        author="Tejas",
        documentation_url="https://github.com/meta-pytorch/OpenEnv",
    )
