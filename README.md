---
title: Sec OpenEnv
emoji: 📉
colorFrom: pink
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: OpenEnv-compatible env for cybersecurity vulnerability triag
---

<img width="36" height="36" alt="Cyber triage" src="assets/logo.svg" /> **Cyber Vulnerability Triage Environment**

![Docker](https://img.shields.io/badge/Docker-ready-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![OpenEnv](https://img.shields.io/badge/OpenEnv-compatible-slategray)

A compact, deterministic benchmark for **web security alert triage**. Each episode looks like a real analyst queue item (suspicious HTTP request + operational context). The agent investigates via structured actions, then submits a final triage decision:

- **vulnerability type** (safe / XSS / SQLi / command injection / traversal)
- **severity**
- **response action** (allow / block / sanitize / monitor)
- **explanation**

## Quick start

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
```

Run a baseline rollout (heuristic fallback if no token is set):

```bash
python inference.py
```

Run the API server:

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Smoke test:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -H 'Content-Type: application/json' -d '{"task":"hard"}'
```

### Run with Docker

```bash
docker build -t cyber-openenv .
docker run --rm -p 8000:8000 cyber-openenv
```

## What this environment is

In production, triage is not “attack / not attack in one shot.” Analysts gather evidence, sanity-check context, and pick a safe operational response. This environment turns that workflow into a repeatable loop:

- `reset()` starts a case
- `step()` runs an investigation action or submits the final triage
- `state()` exposes progress

The observation surface intentionally includes “queue context” (service, tier, priority, impact notes, detection source, handoff) so agents must act like analysts, not like regex matchers.

## Client usage

The repo mirrors the standard OpenEnv environment package shape, so once installed you can use the typed client directly:

```python
import asyncio
from cyber_vulnerability_triage import CyberVulnerabilityTriageEnv


async def main():
    async with CyberVulnerabilityTriageEnv(base_url="http://localhost:8000") as env:
        result = await env.reset(task="hard")
        print(result.observation.request_id)

        result = await env.inspect_payload()
        print(result.observation.evidence_log)

asyncio.run(main())
```

## Tasks

Three tasks scale expectations:

- **`easy`**: vulnerability family
- **`medium`**: vulnerability + severity (encourages multiple evidence sources)
- **`hard`**: full workflow (type + severity + response action + explanation)

Definitions live in [`env/tasks.py`](env/tasks.py).

## Actions and decision space

**Investigation** actions:

- `inspect_payload`
- `decode_obfuscation`
- `review_history`
- `check_source_reputation`
- `inspect_asset_context`
- `consult_playbook`

**Terminal** action:

- `submit_triage` with `vulnerability_type`, `severity`, `response_action`, and `explanation`

Types and schemas are in [`env/models.py`](env/models.py).

## Data and grading

- **Dataset**: 12 deterministic cases in [`env/data.py`](env/data.py)
- **Graders**: deterministic scoring in [`graders/`](graders/)
- **Reward**: combines investigation utility + final decision quality (see [`env/reward.py`](env/reward.py))

## OpenEnv compatibility (optional)

[OpenEnv](https://github.com/meta-pytorch/OpenEnv) standardizes environment servers around `reset`, `step`, `state`, schemas, metadata, and websockets.

This repo works in two modes:

- **OpenEnv integrated** (recommended when you’re using OpenEnv tooling):

```bash
python -m pip install -e ".[openenv]"
```

- **Fallback mode** when `openenv-core` is not installed (still supports `/reset`, `/step`, `/state`, `/metadata`, `/health`).

## Repository layout

```text
.
├── __init__.py               # package exports (`import cyber_vulnerability_triage`)
├── client.py                 # typed OpenEnv client
├── models.py                 # public action / observation / state models
├── openenv.yaml              # OpenEnv manifest
├── pyproject.toml            # package + dependency configuration
├── server/
│   ├── app.py                # canonical FastAPI app
│   ├── cyber_vulnerability_triage_environment.py
│   ├── fallback_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── env/                      # benchmark implementation internals
├── graders/                  # deterministic scoring
├── agent/                    # baseline agent
├── outputs/
│   ├── logs/
│   └── evals/
├── docs/                     # lightweight OpenEnv-style docs tree
├── inference.py              # baseline evaluation driver
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

## LLM configuration (optional)

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-token"
```

## License

See [`LICENSE`](LICENSE).

## Quick start (local)

Install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```

Run baseline scoring:

```bash
python inference.py
```

Required environment variables for LLM-backed inference:

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-token"
```

If `HF_TOKEN` is not set, the baseline falls back to a deterministic heuristic agent so local validation can still run end to end.

## Run as an API (FastAPI)

The canonical OpenEnv server entrypoint is `server/app.py`.

Run it:

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Try it:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -H 'Content-Type: application/json' -d '{"task":"hard"}'
```

For deployment checks, `/health` should return `200`, and `POST /reset` should return the first typed observation payload for the requested task.

## Docker

Build:

```bash
docker build -t cyber-openenv .
```

Run API:

```bash
docker run --rm -p 8000:8000 cyber-openenv
```

Run baseline inside docker:

```bash
docker run --rm cyber-openenv python inference.py
```

## Examples

- [`examples/local_cyber_triage.py`](examples/local_cyber_triage.py) shows a minimal end-to-end local interaction loop.
- [`server/README.md`](server/README.md) documents the deployment-facing server files.

## Submission notes

- `inference.py` is in the repo root as required.
- Stdout uses only structured `[START]`, `[STEP]`, and `[END]` logs for evaluator parsing.
- `openenv.yaml` follows the current OpenEnv `spec_version: 1` manifest format.
- The environment exposes three graded tasks: `easy`, `medium`, and `hard`.
- Reward-bearing score components are clamped into the open interval `(0, 1)`.
