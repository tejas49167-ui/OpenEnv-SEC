from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

VulnerabilityType = Literal[
    "safe",
    "xss",
    "sql_injection",
    "command_injection",
    "path_traversal",
]
SeverityLevel = Literal["none", "low", "medium", "high", "critical"]
ResponseAction = Literal["allow", "block", "sanitize"]
TaskName = Literal["easy", "medium", "hard"]


class RequestExample(BaseModel):
    request_id: str
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


class Observation(BaseModel):
    task: TaskName
    request_id: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: str
    source_ip: str
    user_agent: str
    instructions: str
    allowed_vulnerabilities: List[VulnerabilityType]
    allowed_severities: List[SeverityLevel]
    allowed_actions: List[ResponseAction]


class Action(BaseModel):
    vulnerability_type: VulnerabilityType
    severity: SeverityLevel
    response_action: ResponseAction
    explanation: str = ""


class Reward(BaseModel):
    score: float
    vulnerability_score: float = 0.0
    severity_score: float = 0.0
    action_score: float = 0.0
    explanation_score: float = 0.0
    penalty: float = 0.0
    feedback: str


class StepInfo(BaseModel):
    task: TaskName
    request_id: str
    ground_truth_vulnerability: VulnerabilityType
    ground_truth_severity: SeverityLevel
    ground_truth_action: ResponseAction
    grader_name: str
    component_scores: Dict[str, float]


class EnvironmentState(BaseModel):
    current_task: TaskName = "easy"
    current_index: int = 0
    episode_count: int = 0
    completed: bool = False
    last_request_id: Optional[str] = None
    last_reward: Optional[Reward] = None

