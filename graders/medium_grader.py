from __future__ import annotations

from typing import Dict, Tuple

from env.models import Action, EnvironmentState, RequestExample
from env.scoring import clamp_open_unit_interval
from graders.base_grader import BaseGrader


class MediumGrader(BaseGrader):
    name = "medium_grader"
    task_name = "medium"

    def grade(
        self,
        action: Action,
        example: RequestExample,
        state: EnvironmentState,
    ) -> Tuple[float, Dict[str, float], str]:
        vulnerability = 0.45 if action.vulnerability_type == example.vulnerability_type else 0.0
        severity = 0.30 if action.severity == example.severity else 0.0
        investigation = 0.15 * self.investigation_credit(example, state)
        efficiency = 0.10 * self.efficiency_credit(state)
        safety_penalty = 0.25 if example.vulnerability_type != "safe" and action.response_action == "allow" else 0.0
        terminal = vulnerability + severity + investigation + efficiency
        score = clamp_open_unit_interval(terminal - safety_penalty)
        feedback = (
            f"Medium triage complete for {example.request_id}. "
            f"severity_match={severity > 0}, artifacts={len(state.revealed_artifacts)}."
        )
        return score, {
            "step": 0.0,
            "terminal": terminal,
            "investigation": investigation,
            "decision": vulnerability + severity,
            "efficiency": efficiency,
            "safety_penalty": safety_penalty,
        }, feedback
