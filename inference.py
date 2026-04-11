from __future__ import annotations

import json
import os

from sec_openenv.evaluation import evaluate_models


def main() -> None:
    environment = os.getenv("SEC_OPENENV_ENV", "cyber-vulnerability-triage")
    task = os.getenv("SEC_OPENENV_TASK", "hard")
    raw_models = os.getenv("SEC_OPENENV_MODELS", os.getenv("MODEL_NAME", "gpt-4o-mini"))
    models = [model.strip() for model in raw_models.split(",") if model.strip()]
    episodes = int(os.getenv("SEC_OPENENV_EPISODES", "3"))
    summaries = evaluate_models(environment, models, task=task, episodes=episodes)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
