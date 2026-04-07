from __future__ import annotations

from typing import Dict, Tuple

from env.models import Action, EnvironmentState, RequestExample
from env.scoring import clamp_open_unit_interval
from graders.base_grader import BaseGrader


class EasyGrader(BaseGrader):
    name = "easy_grader"
    task_name = "easy"

    def grade(
        self,
        action: Action,
        example: RequestExample,
        state: EnvironmentState,
    ) -> Tuple[float, Dict[str, float], str]:
        decision = 0.75 if action.vulnerability_type == example.vulnerability_type else 0.0
        safety = 0.15 if action.response_action == example.recommended_action or example.vulnerability_type == "safe" else 0.0
        investigation = 0.10 * self.investigation_credit(example, state)
        safety_penalty = 0.20 if example.vulnerability_type != "safe" and action.response_action == "allow" else 0.0
        terminal = decision + safety + investigation
        score = clamp_open_unit_interval(terminal - safety_penalty)
        feedback = (
            f"Easy triage complete for {example.request_id}. "
            f"Vulnerability match={decision > 0}, investigation_credit={investigation:.2f}."
        )
        return score, {
            "step": 0.0,
            "terminal": terminal,
            "investigation": investigation,
            "decision": decision + safety,
            "efficiency": 0.0,
            "safety_penalty": safety_penalty,
        }, feedback
