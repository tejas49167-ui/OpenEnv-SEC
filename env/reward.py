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
    return grader.build_reward(action, example)

