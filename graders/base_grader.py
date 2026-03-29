from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Tuple

from env.models import Action, RequestExample, Reward


class BaseGrader(ABC):
    name: str

    @abstractmethod
    def grade(self, action: Action, example: RequestExample) -> Tuple[float, Dict[str, float], str]:
        raise NotImplementedError

    def build_reward(self, action: Action, example: RequestExample) -> Reward:
        score, components, feedback = self.grade(action, example)
        return Reward(
            score=score,
            vulnerability_score=components.get("vulnerability", 0.0),
            severity_score=components.get("severity", 0.0),
            action_score=components.get("action", 0.0),
            explanation_score=components.get("explanation", 0.0),
            penalty=components.get("penalty", 0.0),
            feedback=feedback,
        )

