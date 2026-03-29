from __future__ import annotations

from statistics import mean
from typing import Dict, List

from agent.baseline_agent import BaselineTriageAgent
from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import TaskName


def run_task(task: TaskName, episodes: int = 10) -> Dict[str, float]:
    env = CyberVulnerabilityTriageEnvironment(task=task)
    agent = BaselineTriageAgent()
    scores: List[float] = []

    for _ in range(episodes):
        observation = env.reset(task)
        action = agent.decide(observation)
        _, reward, _, _ = env.step(action)
        scores.append(reward.score)

    return {
        "episodes": float(episodes),
        "average_score": mean(scores),
        "min_score": min(scores),
        "max_score": max(scores),
    }


def main() -> None:
    task_order: List[TaskName] = ["easy", "medium", "hard"]
    results = {task: run_task(task) for task in task_order}
    overall_average = mean(result["average_score"] for result in results.values())

    print("Cybersecurity Web Vulnerability Triage Environment")
    print("=" * 52)
    for task in task_order:
        result = results[task]
        print(
            f"{task.upper():<6} episodes={int(result['episodes'])} "
            f"avg={result['average_score']:.3f} "
            f"min={result['min_score']:.3f} max={result['max_score']:.3f}"
        )
    print("-" * 52)
    print(f"OVERALL avg={overall_average:.3f}")


if __name__ == "__main__":
    main()

