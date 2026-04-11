from __future__ import annotations

from typing import Dict

from pydantic import BaseModel

from env.models import TaskName


class TaskDefinition(BaseModel):
    name: TaskName
    description: str
    instructions: str
    max_steps: int
    required_artifacts_for_full_credit: int


TASKS: Dict[TaskName, TaskDefinition] = {
    "easy": TaskDefinition(
        name="easy",
        description="Classify whether the request is safe or malicious and name the vulnerability family.",
        instructions=(
            "Investigate the alert and submit the most likely vulnerability type. "
            "You should usually inspect the payload before deciding. Severity and "
            "response action must still be valid, but grading focuses mostly on the "
            "vulnerability decision and avoiding clearly unsafe triage."
        ),
        max_steps=3,
        required_artifacts_for_full_credit=1,
    ),
    "medium": TaskDefinition(
        name="medium",
        description="Perform analyst triage with vulnerability classification and severity assessment.",
        instructions=(
            "Investigate the request, gather supporting evidence, and submit the "
            "vulnerability type plus severity. Strong solutions inspect at least two "
            "distinct sources of evidence before deciding."
        ),
        max_steps=5,
        required_artifacts_for_full_credit=2,
    ),
    "hard": TaskDefinition(
        name="hard",
        description="Run a full alert-investigation workflow and choose the safest operational response.",
        instructions=(
            "Act like a web security analyst. Use the available investigation tools, "
            "corroborate the signal with context, then submit vulnerability type, "
            "severity, response action, and a concise analyst explanation."
        ),
        max_steps=6,
        required_artifacts_for_full_credit=3,
    ),
}
