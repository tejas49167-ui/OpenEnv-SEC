from __future__ import annotations

from graders.easy_grader import EasyGrader
from graders.hard_grader import HardGrader
from graders.medium_grader import MediumGrader

from env.models import Action, EnvironmentState, RequestExample, Reward, TaskName


GRADERS = {
    "easy": EasyGrader(),
    "medium": MediumGrader(),
    "hard": HardGrader(),
}


def compute_reward(task: TaskName, action: Action, example: RequestExample, state: EnvironmentState) -> Reward:
    grader = GRADERS[task]
    reward = grader.build_reward(action, example, state)
    reward.score = max(0.0, min(1.0, reward.score))
    reward.step_score = max(0.0, min(1.0, reward.step_score))
    reward.terminal_score = max(0.0, min(1.0, reward.terminal_score))
    reward.investigation_score = max(0.0, min(1.0, reward.investigation_score))
    reward.decision_score = max(0.0, min(1.0, reward.decision_score))
    reward.efficiency_score = max(0.0, min(1.0, reward.efficiency_score))
    reward.safety_penalty = max(0.0, min(1.0, reward.safety_penalty))
    return reward
