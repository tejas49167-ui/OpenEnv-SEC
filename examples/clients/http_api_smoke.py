from __future__ import annotations

import json

import requests

BASE_URL = "http://localhost:8000"


def main() -> None:
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    health.raise_for_status()
    print("health:", health.json())

    reset = requests.post(f"{BASE_URL}/reset", json={"task": "medium"}, timeout=10)
    reset.raise_for_status()
    payload = reset.json()
    observation = payload["observation"]
    print("request_id:", observation["request_id"])
    print("task:", observation["task"])
    print("available_actions:", json.dumps(observation["available_action_types"]))


if __name__ == "__main__":
    main()
