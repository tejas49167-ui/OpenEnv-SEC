from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sec_openenv import run_episode


def main() -> None:
    trace = run_episode("cyber-vulnerability-triage", task="hard", seed=2)
    print(f"environment: {trace.environment}")
    print(f"task: {trace.task}")
    print(f"steps: {trace.steps}")
    print(f"final_score: {trace.score}")
    print(f"success: {trace.success}")
    print(f"final_request: {trace.final_observation['request_id']}")


if __name__ == "__main__":
    main()
