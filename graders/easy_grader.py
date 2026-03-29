from __future__ import annotations

from typing import Dict, Tuple

from env.models import Action, RequestExample
from graders.base_grader import BaseGrader


class EasyGrader(BaseGrader):
    name = "easy_grader"

    def grade(self, action: Action, example: RequestExample) -> Tuple[float, Dict[str, float], str]:
        vulnerability = 1.0 if action.vulnerability_type == example.vulnerability_type else 0.0
        score = vulnerability
        feedback = "Correct vulnerability type." if vulnerability else "Incorrect vulnerability type."
        return score, {
            "vulnerability": vulnerability,
            "severity": 0.0,
            "action": 0.0,
            "explanation": 0.0,
            "penalty": 0.0,
        }, feedback

