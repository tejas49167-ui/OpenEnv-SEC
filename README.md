#                     Cyber OpenEnv: Web Alert Triage

![Alt Text](https://wallpaperaccess.com/full/5996656.jpg)

This repo is a complete **OpenEnv-style environment** that simulates a real task a SOC/AppSec analyst does every day: **triaging suspicious HTTP requests**.

Instead of making a one-shot “XSS vs not-XSS” guess, an agent must **investigate** (payload, decoding, history, reputation, asset context, playbook) and then submit a **final operational decision**.

## What you can do with it

- Train/evaluate agents on a **multi-step** security workflow.
- Compare prompts/agents/models in a **deterministic** setting (same cases, same graders).
- Measure not only correctness, but also **safety** (e.g., penalize “allow” on clearly malicious traffic) and **process** (evidence gathering).

## Environment API (reset / step / state)

The core environment lives in `env/environment.py` and exposes:

- `reset(task)` → starts a new alert case
- `step(action)` → advances the investigation or submits a decision
- `state()` → returns the internal state (episode counters, steps, etc.)

An episode starts with an alert summary and raw request fields. Additional context is only revealed when the agent takes investigation actions.

## Observation space

The environment returns a typed Pydantic `Observation` (`env/models.py`). Key fields:

- **Task**: `task` (id) + `task_label` (human-readable)
- **Request**: `request_id`, `queue`, `title`, `method`, `path`, `headers`, `query_params`, `body`, `source_ip`, `user_agent`
- **Agent guidance**: `instructions`
- **Progress**: `steps_taken`, `remaining_steps`
- **Evidence bookkeeping**: `available_artifacts`, `collected_artifacts`, `evidence_log`
- **Allowed values**: `available_action_types`, `allowed_vulnerabilities`, `allowed_severities`, `allowed_actions`

## Action space

Agents submit a typed Pydantic `Action` (`env/models.py`):

- `action_type`
- `vulnerability_type` (nullable unless submitting)
- `severity` (nullable unless submitting)
- `response_action` (nullable unless submitting)
- `explanation`

Supported `action_type` values:

- `inspect_payload`
- `decode_obfuscation`
- `review_history`
- `check_source_reputation`
- `inspect_asset_context`
- `consult_playbook`
- `submit_triage`

Supported vulnerability classes:

- `safe`
- `xss`
- `sql_injection`
- `command_injection`
- `path_traversal`

Supported response actions:

- `allow`
- `block`
- `sanitize`
- `monitor`

## Tasks (difficulty progression)

Task definitions are in `env/tasks.py`.

- **Easy (Quick classification)**: choose the most likely vulnerability family (grading focuses mainly on correct type + avoiding obviously unsafe calls)
- **Medium (Severity + evidence)**: choose vulnerability type **and** severity; stronger solutions gather multiple pieces of evidence
- **Hard (Full triage workflow)**: complete a full analyst-style flow and choose the safest operational response with a concise explanation

## Dataset

The environment ships with **12 deterministic cases** in `env/data.py`. Each case includes:

- raw HTTP request fields
- ground truth vulnerability type + severity
- recommended operational action
- explanation keywords
- “hidden” analyst artifacts revealed by investigation actions

## Reward shaping (why it’s not just a final grade)

Rewards are designed to provide signal during the trajectory:

- investigation steps give positive reward when they reveal **new** evidence
- “useful” investigation actions receive higher step reward
- repeated inspections are penalized
- terminal grading scores the final triage decision (and can apply **safety penalties**)

Reward/grading logic is implemented in `env/reward.py` and the task-specific graders.

## Graders (deterministic, 0.0–1.0)

Graders live in `graders/`:

- `graders/easy_grader.py`
- `graders/medium_grader.py`
- `graders/hard_grader.py`

All graders are deterministic and produce a final score in the `[0.0, 1.0]` range.

## Baseline agent + reproducible scores

The baseline agent is in `agent/baseline_agent.py`.

Run the baseline evaluation:

```bash
python inference.py
```

Example output (will be reproducible locally because cases + graders are deterministic):

```text
Easy (Quick classification)    episodes=12 avg=1.000 min=1.000 max=1.000 avg_steps=2.33
Medium (Severity + evidence)   episodes=12 avg=0.927 min=0.865 max=0.940 avg_steps=4.33
Hard (Full triage workflow)    episodes=12 avg=0.953 min=0.917 max=0.967 avg_steps=5.58
OVERALL avg=0.960
```

### Optional: model-backed inference

If you want the baseline agent to call a model endpoint (OpenAI-compatible), set:

```bash
export API_BASE_URL="https://your-openai-compatible-endpoint/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-token"
python inference.py
```

## HTTP API (FastAPI)

The service is defined in `app.py`.

Endpoints:

- `GET /`
- `GET /health`
- `POST /reset`
- `POST /step`
- `GET /state`

Quick demo:

```bash
curl http://localhost:7860/health
curl -X POST http://localhost:7860/reset -H 'Content-Type: application/json' -d '{"task":"hard"}'
```

## Setup (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API server:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 7860
```

## Docker

Build:

```bash
docker build -t cyber-openenv .
```

Run:

```bash
docker run --rm -p 7860:7860 cyber-openenv
```

Run the baseline inside the container:

```bash
docker run --rm cyber-openenv python inference.py
```

## Design notes (why it’s structured this way)

- **Determinism matters**: fixed cases + deterministic graders make it easy to compare agents fairly.
- **Process matters**: the environment rewards evidence collection, not only the final label.
- **Safety matters**: unsafe operational decisions can be penalized even if the label guess is close.

## Project structure

```text
cyber-openenv/
├── agent/
├── env/
├── graders/
├── app.py
├── inference.py
├── openenv.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```
