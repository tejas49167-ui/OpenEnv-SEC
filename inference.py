from __future__ import annotations

import json
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


def emit_block(block_type: str, **fields: object) -> None:
    serialized_fields = " ".join(
        f"{key}={serialize_field(value)}" for key, value in fields.items()
    )
    print(f"[{block_type}] {serialized_fields}", flush=True)


def serialize_field(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if any(character.isspace() for character in text):
        return json.dumps(text)
    return text


def log_start(task: TaskName, episode: int, total_episodes: int) -> None:
    emit_block(
        "START",
        task=task,
        task_label=TASK_LABELS[task],
        episode=episode,
        total_episodes=total_episodes,
    )


def log_step(
    task: TaskName,
    episode: int,
    step: int,
    action_type: str,
    reward: float,
    done: bool,
) -> None:
    emit_block(
        "STEP",
        task=task,
        episode=episode,
        step=step,
        action_type=action_type,
        reward=f"{reward:.3f}",
        done=done,
    )


def log_end(task: TaskName, episode: int, score: float, steps_taken: int) -> None:
    emit_block("END", task=task, episode=episode, score=f"{score:.3f}", steps=steps_taken)


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
            observation, reward, done, _ = env.step(action)
            log_step(task, episode, next_step, action.action_type, reward.score, done)

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

    emit_block("END", task="summary", score=f"{overall_average:.3f}", steps=0)
    for task in task_order:
        result = results[task]
        emit_block(
            "END",
            task=task,
            episodes=int(result["episodes"]),
            average_score=f"{result['average_score']:.3f}",
            min_score=f"{result['min_score']:.3f}",
            max_score=f"{result['max_score']:.3f}",
            average_steps=f"{result['average_steps']:.2f}",
        )


if __name__ == "__main__":
    main()
