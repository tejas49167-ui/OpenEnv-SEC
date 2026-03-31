from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Tuple

from env.models import Action, EnvironmentState, RequestExample, Reward
from env.tasks import TASKS


class BaseGrader(ABC):
    name: str
    task_name: str

    @abstractmethod
    def grade(
        self,
        action: Action,
        example: RequestExample,
        state: EnvironmentState,
    ) -> Tuple[float, Dict[str, float], str]:
        raise NotImplementedError

    def investigation_credit(self, example: RequestExample, state: EnvironmentState) -> float:
        useful_reveals = sum(1 for action in example.useful_actions if self._artifact_for_action(action) in state.revealed_artifacts)
        required = TASKS[self.task_name].required_artifacts_for_full_credit
        return min(1.0, useful_reveals / max(1, required))

    def efficiency_credit(self, state: EnvironmentState) -> float:
        if state.max_steps <= 0:
            return 0.0
        return max(0.0, 1.0 - (max(0, state.steps_taken - 1) / state.max_steps))

    def explanation_credit(self, action: Action, example: RequestExample) -> float:
        if not action.explanation.strip():
            return 0.0
        explanation = action.explanation.lower()
        matched_keywords = sum(1 for keyword in example.explanation_keywords if keyword in explanation)
        mentions_decision = any(
            token in explanation
            for token in ["xss", "sql", "command", "traversal", "safe", "block", "sanitize", "allow", "monitor"]
        )
        return 1.0 if matched_keywords >= 2 and mentions_decision and len(explanation) >= 40 else 0.0

    def build_reward(self, action: Action, example: RequestExample, state: EnvironmentState) -> Reward:
        score, components, feedback = self.grade(action, example, state)
        return Reward(
            score=score,
            step_score=components.get("step", 0.0),
            terminal_score=components.get("terminal", 0.0),
            investigation_score=components.get("investigation", 0.0),
            decision_score=components.get("decision", 0.0),
            efficiency_score=components.get("efficiency", 0.0),
            safety_penalty=components.get("safety_penalty", 0.0),
            feedback=feedback,
        )

    @staticmethod
    def _artifact_for_action(action_type: str) -> str:
        mapping = {
            "inspect_payload": "payload_analysis",
            "decode_obfuscation": "decoded_input",
            "review_history": "traffic_history",
            "check_source_reputation": "source_reputation",
            "inspect_asset_context": "asset_context",
            "consult_playbook": "playbook_guidance",
        }
        return mapping[action_type]
