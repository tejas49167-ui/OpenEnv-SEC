from __future__ import annotations

from typing import Dict, Tuple

from env.models import Action, RequestExample
from graders.base_grader import BaseGrader


class MediumGrader(BaseGrader):
    name = "medium_grader"

    def grade(self, action: Action, example: RequestExample) -> Tuple[float, Dict[str, float], str]:
        vulnerability = 0.5 if action.vulnerability_type == example.vulnerability_type else 0.0
        severity = 0.5 if action.severity == example.severity else 0.0
        score = vulnerability + severity
        feedback = (
            "Correct vulnerability type and severity."
            if score == 1.0
            else (
                "Correct vulnerability type but incorrect severity."
                if vulnerability and not severity
                else "Incorrect vulnerability classification."
            )
        )
        return score, {
            "vulnerability": vulnerability,
            "severity": severity,
            "action": 0.0,
            "explanation": 0.0,
            "penalty": 0.0,
        }, feedback
