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
        mentions_attack_type = any(token in explanation for token in ["xss", "sql", "script", "traversal", "command", "injection"])
        mentions_mitigation = any(token in explanation for token in ["block", "sanitize", "allow"])
        length_ok = len(action.explanation.strip()) >= 40
        if matched_keywords >= 2 and mentions_attack_type and mentions_mitigation and length_ok:
            return 0.1
        return 0.0

    def _penalty(self, action: Action, example: RequestExample) -> float:
        if example.vulnerability_type != "safe" and action.response_action == "allow":
            return 0.4
        if example.vulnerability_type == "safe" and action.response_action == "block":
            return 0.10
        if action.severity != example.severity:
            return 0.05
        return 0.0

    def grade(self, action: Action, example: RequestExample) -> Tuple[float, Dict[str, float], str]:
        vulnerability = 0.4 if action.vulnerability_type == example.vulnerability_type else 0.0
        severity = 0.3 if action.severity == example.severity else 0.0
        response_action = 0.3 if action.response_action == example.recommended_action else 0.0
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
