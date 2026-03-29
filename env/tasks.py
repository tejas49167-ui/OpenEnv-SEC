from __future__ import annotations

from typing import Dict

from pydantic import BaseModel

from env.models import TaskName


class TaskDefinition(BaseModel):
    name: TaskName
    description: str
    instructions: str


TASKS: Dict[TaskName, TaskDefinition] = {
    "easy": TaskDefinition(
        name="easy",
        description="Detect the vulnerability type present in an HTTP request.",
        instructions=(
            "Identify the request as one of: safe, xss, sql_injection, "
            "command_injection, or path_traversal. Severity, action, and explanation "
            "are ignored for task scoring, but you should still return valid fields."
        ),
    ),
    "medium": TaskDefinition(
        name="medium",
        description="Detect the vulnerability type and classify severity.",
        instructions=(
            "Identify the vulnerability type and severity. Valid severities are: "
            "none, low, medium, high, critical. Action and explanation are ignored "
            "for task scoring, but you should still return valid fields."
        ),
    ),
    "hard": TaskDefinition(
        name="hard",
        description="Make a full triage decision including detection, severity, action, and explanation.",
        instructions=(
            "Return the vulnerability type, severity, the best response action "
            "(allow, block, sanitize), and a short explanation grounded in the request."
        ),
    ),
}

