from __future__ import annotations

from typing import Dict, Tuple

from env.models import Action, EnvironmentState, RequestExample
from env.scoring import clamp_open_unit_interval
from graders.base_grader import BaseGrader


class HardGrader(BaseGrader):
    name = "hard_grader"
    task_name = "hard"

    def grade(
        self,
        action: Action,
        example: RequestExample,
        state: EnvironmentState,
    ) -> Tuple[float, Dict[str, float], str]:
        vulnerability = 0.30 if action.vulnerability_type == example.vulnerability_type else 0.0
        severity = 0.20 if action.severity == example.severity else 0.0
        response_action = 0.20 if action.response_action == example.recommended_action else 0.0
        investigation = 0.15 * self.investigation_credit(example, state)
        explanation = 0.10 * self.explanation_credit(action, example)
        efficiency = 0.05 * self.efficiency_credit(state)

        safety_penalty = 0.0
        if example.vulnerability_type != "safe" and action.response_action == "allow":
            safety_penalty += 0.30
        if example.vulnerability_type == "safe" and action.response_action == "block":
            safety_penalty += 0.10
        if action.severity != example.severity:
            safety_penalty += 0.05

        terminal = (
            vulnerability + severity + response_action + investigation + explanation + efficiency
        )
        score = clamp_open_unit_interval(terminal - safety_penalty)
        feedback = (
            f"Hard triage complete for {example.request_id}. "
            f"response_match={response_action > 0}, explanation_credit={explanation:.2f}."
        )
        return (
            score,
            {
                "step": 0.0,
                "terminal": terminal,
                "investigation": investigation,
                "decision": vulnerability + severity + response_action + explanation,
                "efficiency": efficiency,
                "safety_penalty": safety_penalty,
            },
            feedback,
        )
