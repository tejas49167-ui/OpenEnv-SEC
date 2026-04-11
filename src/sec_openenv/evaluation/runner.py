from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any

from sec_openenv.framework.registry import create_environment, get_environment


@dataclass
class EpisodeTrace:
    environment: str
    task: str
    model: str
    success: bool
    score: float
    steps: int
    reward_trace: list[float]
    final_observation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_openai_client() -> Any:
    try:
        from openai import OpenAI
    except ImportError:
        return None
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
    if not api_key:
        return None
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL")
    kwargs: dict[str, str] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def run_episode(
    env_name: str,
    *,
    task: str | None = None,
    seed: int | None = None,
    model_name: str = "gpt-4o-mini",
    client: Any = None,
    agent: Any | None = None,
) -> EpisodeTrace:
    descriptor = get_environment(env_name)
    environment = create_environment(env_name, task=task or None)
    agent_instance = agent or descriptor.load_default_agent()(client=client, model_name=model_name)

    observation = environment.reset(task=task, seed=seed)
    rewards: list[float] = []

    while not observation.done:
        next_action = agent_instance.decide(observation)
        observation = environment.step(next_action)
        reward = float(
            (observation.metadata.get("reward") or {}).get("score", observation.reward or 0.0)
        )
        rewards.append(reward)

    final_reward = float(
        (observation.metadata.get("reward") or {}).get("score", observation.reward or 0.0)
    )
    return EpisodeTrace(
        environment=descriptor.slug,
        task=getattr(observation, "task", task or "default"),
        model=model_name,
        success=final_reward >= 0.5,
        score=final_reward,
        steps=getattr(
            environment.state, "step_count", getattr(environment.state, "steps_taken", 0)
        ),
        reward_trace=rewards,
        final_observation=observation.model_dump(),
    )


def evaluate_models(
    env_name: str,
    model_names: list[str],
    *,
    task: str | None = None,
    episodes: int = 3,
) -> list[dict[str, Any]]:
    client = build_openai_client()
    summaries: list[dict[str, Any]] = []

    for model_name in model_names:
        traces = [
            run_episode(
                env_name,
                task=task,
                seed=index,
                model_name=model_name,
                client=client,
            )
            for index in range(episodes)
        ]
        summaries.append(
            {
                "environment": env_name,
                "task": task or traces[0].task,
                "model": model_name,
                "episodes": episodes,
                "average_score": round(mean(trace.score for trace in traces), 3),
                "average_steps": round(mean(trace.steps for trace in traces), 2),
                "success_rate": round(mean(1.0 if trace.success else 0.0 for trace in traces), 3),
            }
        )
    return summaries
