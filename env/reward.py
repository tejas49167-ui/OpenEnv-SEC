from __future__ import annotations

from graders.easy_grader import EasyGrader
from graders.hard_grader import HardGrader
from graders.medium_grader import MediumGrader

from env.models import Action, RequestExample, Reward, TaskName


GRADERS = {
    "easy": EasyGrader(),
    "medium": MediumGrader(),
    "hard": HardGrader(),
}


def compute_reward(task: TaskName, action: Action, example: RequestExample) -> Reward:
    grader = GRADERS[task]
    reward = grader.build_reward(action, example)
    reward.score = max(0.0, min(1.0, reward.score))
    reward.vulnerability_score = max(0.0, min(1.0, reward.vulnerability_score))
    reward.severity_score = max(0.0, min(1.0, reward.severity_score))
    reward.action_score = max(0.0, min(1.0, reward.action_score))
    reward.explanation_score = max(0.0, min(1.0, reward.explanation_score))
    reward.penalty = max(0.0, min(1.0, reward.penalty))
    return reward
