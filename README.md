# Cybersecurity Alert Triage OpenEnv

## Overview

This project is a multi-step OpenEnv environment for **web application security alert triage**. The agent plays the role of a security analyst reviewing suspicious HTTP requests, gathering evidence, and making an operational decision.

Unlike a one-shot classifier, this environment requires the agent to investigate a case over several steps:

- inspect the request payload
- decode obfuscated input
- review recent request history
- check source reputation
- inspect asset context
- consult the internal playbook
- submit a final triage decision

This mirrors a real SOC / AppSec workflow where analysts rarely decide on raw payloads alone.

## Why This Is Useful

Security teams routinely triage borderline web alerts:

- Is this request actually malicious or just suspicious-looking?
- Is it XSS, SQL injection, command injection, or path traversal?
- How severe is it in the context of the asset?
- Should the system allow it, sanitize it, block it, or monitor it?

This environment is designed for training and evaluating agents on that workflow in a deterministic, reproducible setting.

## Environment Design

The core environment is implemented in [`env/environment.py`](/home/tejas/cyber-openenv/env/environment.py) and follows the standard OpenEnv lifecycle:

- `reset(task)` starts a fresh alert case
- `step(action)` advances the investigation
- `state()` returns the current environment state

Each episode begins with a realistic alert summary and raw HTTP request data. Hidden context is revealed only when the agent takes the corresponding investigation action.

## Observation Space

The environment returns a typed Pydantic `Observation` with:

- `task`
- `request_id`
- `queue`
- `title`
- `method`
- `path`
- `headers`
- `query_params`
- `body`
- `source_ip`
- `user_agent`
- `instructions`
- `steps_taken`
- `remaining_steps`
- `available_artifacts`
- `collected_artifacts`
- `evidence_log`
- `available_action_types`
- `allowed_vulnerabilities`
- `allowed_severities`
- `allowed_actions`

## Action Space

The agent must return a typed Pydantic `Action`:

- `action_type`
- `vulnerability_type`
- `severity`
- `response_action`
- `explanation`

Supported `action_type` values:

- `inspect_payload`
- `decode_obfuscation`
- `review_history`
- `check_source_reputation`
- `inspect_asset_context`
- `consult_playbook`
- `submit_triage`

For investigation actions, the decision fields can be `null`. For `submit_triage`, the agent must provide a full final decision.

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

## Tasks

Three deterministic tasks are included:

- `easy`: classify whether the alert is safe or malicious and identify the vulnerability family
- `medium`: classify vulnerability type and severity using multiple pieces of evidence
- `hard`: complete a full analyst workflow with evidence gathering, severity, response action, and explanation

Task definitions live in [`env/tasks.py`](/home/tejas/cyber-openenv/env/tasks.py).

## Dataset

The environment ships with 12 realistic web-alert cases in [`env/data.py`](/home/tejas/cyber-openenv/env/data.py), covering:

- reflected and stored XSS
- SQL injection
- command injection
- path traversal
- benign traffic that includes misleading security-like terms

Every case includes:

- raw HTTP request fields
- ground-truth vulnerability type
- ground-truth severity
- recommended operational action
- explanation keywords
- hidden analyst artifacts for each investigation tool

## Reward Function

Rewards are designed to provide signal across the full trajectory:

- positive step reward for revealing new evidence
- higher credit when the agent investigates the most relevant artifacts
- terminal grading based on task difficulty
- efficiency credit for solving cases without wasting steps
- penalties for unsafe decisions such as allowing a malicious request

This creates a better learning signal than a pure one-step binary grade.

## Graders

Deterministic graders are implemented in [`graders/easy_grader.py`](/home/tejas/cyber-openenv/graders/easy_grader.py), [`graders/medium_grader.py`](/home/tejas/cyber-openenv/graders/medium_grader.py), and [`graders/hard_grader.py`](/home/tejas/cyber-openenv/graders/hard_grader.py).

High-level scoring:

- `easy`: emphasizes vulnerability identification and avoiding unsafe allows
- `medium`: scores vulnerability, severity, evidence quality, and efficiency
- `hard`: scores full triage quality, explanation quality, workflow quality, and safety

All graders are deterministic and return scores in the `[0.0, 1.0]` range.

## Baseline Agent

The baseline agent in [`agent/baseline_agent.py`](/home/tejas/cyber-openenv/agent/baseline_agent.py) supports two modes:

- OpenAI-compatible inference using `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`
- deterministic heuristic fallback when no model endpoint is configured

The baseline performs multi-step investigation before submitting a final decision.

## Baseline Scores

Current local deterministic baseline:

```text
EASY   episodes=12 avg=1.000 min=1.000 max=1.000 avg_steps=2.33
MEDIUM episodes=12 avg=0.927 min=0.865 max=0.940 avg_steps=4.33
HARD   episodes=12 avg=0.953 min=0.917 max=0.967 avg_steps=5.58
OVERALL avg=0.960
```

These scores are produced by:

```bash
python inference.py
```

## HTTP API

A lightweight FastAPI server is exposed from [`app.py`](/home/tejas/cyber-openenv/app.py) for deployment and validation.

Available endpoints:

- `GET /`
- `GET /health`
- `POST /reset`
- `POST /step`
- `GET /state`

Example:

```bash
curl http://localhost:7860/
curl -X POST http://localhost:7860/reset -H 'Content-Type: application/json' -d '{"task":"hard"}'
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running Inference

Deterministic local baseline:

```bash
python inference.py
```

With an OpenAI-compatible endpoint:

```bash
export API_BASE_URL="https://your-openai-compatible-endpoint/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-token"
python inference.py
```

## Running The Service

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Docker

Build:

```bash
docker build -t cyber-openenv .
```

Run the service:

```bash
docker run --rm -p 7860:7860 cyber-openenv
```

Run the inference script inside the container if you want a score check:

```bash
docker run --rm cyber-openenv python inference.py
```

## Project Structure

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
