from __future__ import annotations

from agent.baseline_agent import BaselineTriageAgent
from env.environment import CyberVulnerabilityTriageEnvironment


def main() -> None:
    env = CyberVulnerabilityTriageEnvironment(task="hard")
    agent = BaselineTriageAgent()

    observation = env.reset(task="hard", seed=2)
    print(f"starting request={observation.request_id}")

    while not observation.done:
        action = agent.decide(observation)
        print("action:", action.action_type)
        observation = env.step(action)

    reward = observation.metadata.get("reward", {})
    print("final_score:", reward.get("score", observation.reward))
    print("feedback:", reward.get("feedback", ""))


if __name__ == "__main__":
    main()
