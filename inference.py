from __future__ import annotations

from statistics import mean
from typing import Dict, List

from agent.baseline_agent import BaselineTriageAgent
from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import TASK_LABELS
from env.models import TaskName


def run_task(task: TaskName, episodes: int = 12) -> Dict[str, float]:
    env = CyberVulnerabilityTriageEnvironment(task=task)
    agent = BaselineTriageAgent()
    final_scores: List[float] = []
    step_counts: List[int] = []

    for _ in range(episodes):
        observation = env.reset(task)
        done = False
        reward = None

        while not done:
            action = agent.decide(observation)
            observation, reward, done, _ = env.step(action)

        assert reward is not None
        final_scores.append(reward.score)
        step_counts.append(env.state().steps_taken)

    return {
        "episodes": float(episodes),
        "average_score": mean(final_scores),
        "min_score": min(final_scores),
        "max_score": max(final_scores),
        "average_steps": mean(step_counts),
    }


def main() -> None:
    task_order: List[TaskName] = ["easy", "medium", "hard"]
    results = {task: run_task(task) for task in task_order}
    overall_average = mean(result["average_score"] for result in results.values())

    print("Cybersecurity Alert Triage OpenEnv")
    print("-" * 52)
    for task in task_order:
        result = results[task]
        label = TASK_LABELS[task]
        print(
            f"{label:<30} episodes={int(result['episodes'])} "
            f"avg={result['average_score']:.3f} "
            f"min={result['min_score']:.3f} max={result['max_score']:.3f} "
            f"avg_steps={result['average_steps']:.2f}"
        )
    print("-" * 52)
    print(f"OVERALL avg={overall_average:.3f}")


if __name__ == "__main__":
    main()
