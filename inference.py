from __future__ import annotations

import json
import os
from statistics import mean
from typing import Dict, List, Optional

from openai import OpenAI

from agent.baseline_agent import BaselineTriageAgent
from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import TaskName

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
BENCHMARK = "cyber-vulnerability-triage"
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
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if any(character.isspace() for character in text):
        return json.dumps(text)
    return text


def log_start(task: TaskName) -> None:
    emit_block(
        "START",
        task=task,
        env=BENCHMARK,
        model=MODEL_NAME,
    )


def log_step(
    step: int,
    action: str,
    reward: float,
    done: bool,
    error: Optional[str],
) -> None:
    emit_block(
        "STEP",
        step=step,
        action=action,
        reward=f"{reward:.3f}",
        done=done,
        error=error,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    emit_block(
        "END",
        success=success,
        steps=steps,
        score=f"{score:.3f}",
        rewards=[round(reward, 3) for reward in rewards],
    )


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

    for _ in range(episodes):
        log_start(task)
        observation = env.reset(task=task)
        done = False
        final_reward = None
        rewards: List[float] = []
        steps_taken = 0

        while not done:
            action = agent.decide(observation)
            next_step = env.state.steps_taken + 1
            observation = env.step(action)
            reward_payload = observation.metadata.get("reward") or {}
            reward_score = float(reward_payload.get("score", observation.reward or 0.0))
            rewards.append(reward_score)
            steps_taken = next_step
            log_step(
                step=next_step,
                action=action.model_dump_json(exclude={"metadata"}),
                reward=reward_score,
                done=observation.done,
                error=None,
            )
            done = observation.done
            final_reward = observation

        assert final_reward is not None
        final_reward_payload = final_reward.metadata.get("reward") or {}
        score = float(final_reward_payload.get("score", final_reward.reward or 0.0))
        final_scores.append(score)
        step_counts.append(steps_taken)
        log_end(success=score >= 0.5, steps=steps_taken, score=score, rewards=rewards)

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
    for task in task_order:
        result = results[task]
        print(
            (
                f"# summary task={task} episodes={int(result['episodes'])} "
                f"average_score={result['average_score']:.3f} "
                f"min_score={result['min_score']:.3f} "
                f"max_score={result['max_score']:.3f} "
                f"average_steps={result['average_steps']:.2f}"
            ),
            file=os.sys.stderr,
            flush=True,
        )


if __name__ == "__main__":
    main()
