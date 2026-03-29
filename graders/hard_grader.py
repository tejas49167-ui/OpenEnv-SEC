from __future__ import annotations

from typing import Dict, Tuple

from env.models import Action, RequestExample
from graders.base_grader import BaseGrader


class HardGrader(BaseGrader):
    name = "hard_grader"

    def _explanation_score(self, action: Action, example: RequestExample) -> float:
        if not action.explanation.strip():
            return 0.0
        explanation = action.explanation.lower()
        matched_keywords = sum(1 for keyword in example.explanation_keywords if keyword in explanation)
        length_ok = len(action.explanation.strip()) >= 20
        keyword_score = min(0.05, 0.025 * matched_keywords)
        return min(0.1, keyword_score + (0.05 if length_ok else 0.0))

    def _penalty(self, action: Action, example: RequestExample) -> float:
        if example.vulnerability_type != "safe" and action.response_action == "allow":
            return 0.25
        if example.vulnerability_type == "safe" and action.response_action == "block":
            return 0.10
        return 0.0

    def grade(self, action: Action, example: RequestExample) -> Tuple[float, Dict[str, float], str]:
        vulnerability = 0.4 if action.vulnerability_type == example.vulnerability_type else 0.0
        severity = 0.3 if action.severity == example.severity else 0.0
        response_action = 0.2 if action.response_action == example.recommended_action else 0.0
        explanation = self._explanation_score(action, example)
        penalty = self._penalty(action, example)
        score = max(0.0, min(1.0, vulnerability + severity + response_action + explanation - penalty))
        feedback = f"Composite hard-task score computed with penalty={penalty:.2f}."
        return score, {
            "vulnerability": vulnerability,
            "severity": severity,
            "action": response_action,
            "explanation": explanation,
            "penalty": penalty,
        }, feedback

