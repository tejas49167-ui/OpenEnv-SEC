from __future__ import annotations

import os
from statistics import mean
from typing import Dict, List, Optional

from openai import OpenAI

from agent.baseline_agent import BaselineTriageAgent
from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import TASK_LABELS
from env.models import TaskName

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional — if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")


def build_client() -> Optional[OpenAI]:
    if not HF_TOKEN:
        return None
    return OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def log_start(task: TaskName, episode: int, total_episodes: int) -> None:
    print(f"START task={task} task_label={TASK_LABELS[task]!r} episode={episode}/{total_episodes}")


def log_step(task: TaskName, episode: int, step: int, action_type: str) -> None:
    print(f"STEP task={task} episode={episode} step={step} action_type={action_type}")


def log_end(task: TaskName, episode: int, score: float, steps_taken: int) -> None:
    print(f"END task={task} episode={episode} score={score:.3f} steps={steps_taken}")


def run_task(
    task: TaskName,
    client: Optional[OpenAI],
    model_name: str,
    episodes: int = 12,
) -> Dict[str, float]:
    env = CyberVulnerabilityTriageEnvironment(task=task)
    agent = BaselineTriageAgent(client=client, model_name=model_name)
    final_scores: List[float] = []
    step_counts: List[int] = []

    for episode in range(1, episodes + 1):
        log_start(task, episode, episodes)
        observation = env.reset(task)
        done = False
        reward = None

        while not done:
            action = agent.decide(observation)
            next_step = env.state().steps_taken + 1
            log_step(task, episode, next_step, action.action_type)
            observation, reward, done, _ = env.step(action)

        assert reward is not None
        steps_taken = env.state().steps_taken
        final_scores.append(reward.score)
        step_counts.append(steps_taken)
        log_end(task, episode, reward.score, steps_taken)

    return {
        "episodes": float(episodes),
        "average_score": mean(final_scores),
        "min_score": min(final_scores),
        "max_score": max(final_scores),
        "average_steps": mean(step_counts),
    }


def main() -> None:
    client = build_client()
    task_order: List[TaskName] = ["easy", "medium", "hard"]
    results = {task: run_task(task, client, MODEL_NAME) for task in task_order}
    overall_average = mean(result["average_score"] for result in results.values())

    print(f"END summary overall_average={overall_average:.3f}")
    for task in task_order:
        result = results[task]
        print(
            "END "
            f"task={task} "
            f"episodes={int(result['episodes'])} "
            f"average_score={result['average_score']:.3f} "
            f"min_score={result['min_score']:.3f} "
            f"max_score={result['max_score']:.3f} "
            f"average_steps={result['average_steps']:.2f}"
        )


if __name__ == "__main__":
    main()
