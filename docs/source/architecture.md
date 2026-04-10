# Architecture

The project keeps the environment idea intentionally focused: every episode is a
security queue item that an agent must investigate and triage.

## Main layers

- `env/` contains the benchmark implementation, deterministic dataset, reward
  logic, and task definitions.
- `graders/` contains task-specific grading logic.
- `client.py`, `models.py`, and `server/` follow the OpenEnv environment package
  pattern used by accepted environments in `OpenEnv`.
- `inference.py` runs a baseline evaluation loop and emits parseable logs for
  hackathon or benchmark automation.

## Why this shape

This layout keeps the cyber triage idea the same while making the repository
look and behave more like a first-class OpenEnv environment package.
