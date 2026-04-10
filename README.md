---
title: Cyber Vulnerability Triage Environment
emoji: shield
colorFrom: slate
colorTo: red
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - cybersecurity
  - evaluation
  - agents
---

# Web alert triage as a multi-step environment

This project is a **small, self-contained benchmark** for how an automated agent handles **application-security alerts**: the kind that land in a queue as “suspicious HTTP traffic,” not as a tidy ML label.

Each **episode** is one request: method, path, headers, body, client hints, plus **queue-style context** (service, tier, priority, impact notes, detection source, handoff text). The agent may **investigate**—pulling artifacts such as payload analysis, history, or playbook guidance—before filing a **final triage**: vulnerability class, severity, operational response, and a short analyst-style explanation.

The point is not “guess the label in one forward pass.” The point is whether the agent **uses evidence**, respects a **step budget**, and ends in a decision that would be **defensible** in a real triage workflow.

## Why this shape (and how it relates to OpenEnv)

[OpenEnv](https://github.com/meta-pytorch/OpenEnv) is a framework for packaging environments behind a consistent **HTTP/WebSocket-style** interface: reset an episode, step with structured actions, read state, expose metadata. **This repository is an independent environment**—same *kind* of layout you see under OpenEnv’s `envs/` packages (manifest + `server/` + client helpers), so it can run **with** OpenEnv tooling when you install the optional dependency, or **without** it via a small fallback server.

Nothing here is meant to restate or replace OpenEnv’s documentation; if you use their stack, follow their guides for deployment and clients. This README only describes **what this environment is** and **how to run it**.

## Tasks

Three difficulty bands exercise progressively stricter expectations:

| Task | What it stresses |
|--------|-------------------|
| `easy` | Vulnerability family (with valid fields; grading centers on classification discipline). |
| `medium` | Vulnerability **and** severity, with incentive to gather corroborating artifacts. |
| `hard` | Full triage: class, severity, **response action**, and explanation grounded in investigation. |

Definitions live in [`env/tasks.py`](env/tasks.py).

## Actions and decision space

**Investigation** (examples): `inspect_payload`, `decode_obfuscation`, `review_history`, `check_source_reputation`, `inspect_asset_context`, `consult_playbook`.

**Terminal**: `submit_triage` with:

- `vulnerability_type`: `safe`, `xss`, `sql_injection`, `command_injection`, `path_traversal`
- `severity`: `none` … `critical`
- `response_action`: `allow`, `block`, `sanitize`, `monitor`
- `explanation`: short justification

Schemas and observation fields are in [`env/models.py`](env/models.py).

## Data and grading

- **12 deterministic cases** in [`env/data.py`](env/data.py): XSS, SQLi, command injection, path traversal, and **benign** traffic that looks “spicy” without being an exploit.
- **Reward** mixes investigation usefulness, efficiency, and task-specific **deterministic graders** in [`graders/`](graders/). Final numeric components are kept in a bounded band suitable for logging and analysis (see [`env/reward.py`](env/reward.py), [`env/scoring.py`](env/scoring.py)).

## Quick start

### Install (virtualenv recommended)

On distributions with an *externally managed* system Python, use a venv first.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Or: `make venv` then `make dev`.

### Run the baseline rollout

```bash
python inference.py
```

Emits structured `[START]`, `[STEP]`, and `[END]` lines for tooling. Without `HF_TOKEN`, a **deterministic heuristic** agent runs so the loop still works offline.

### Run the HTTP server

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Or: `make server`.

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -H 'Content-Type: application/json' -d '{"task":"hard"}'
```

With `openenv-core` installed, you get the usual OpenEnv-style routes (`/reset`, `/step`, `/state`, `/schema`, `/ws`, `/metadata`, `/health`, …). This repo also adds **`/tasks`** and **`/benchmark`** for benchmark metadata.

**Optional extras**

```bash
python -m pip install -e ".[openenv]"       # server integration
python -m pip install -e ".[openenv-core]" # upstream “core” extras (heavier)
```

## Docker

```bash
docker build -t cyber-openenv .
docker run --rm -p 8000:8000 cyber-openenv
docker run --rm cyber-openenv python inference.py
```

Compose: `docker compose up --build api` or `docker compose run --rm eval`.

## Repository layout (OpenEnv-style env package)

```text
.
├── openenv.yaml              # manifest (app entrypoint + port)
├── server/                   # FastAPI app + environment wiring
│   ├── app.py
│   ├── fallback_app.py      # minimal server if openenv-core is absent
│   └── cyber_vulnerability_triage_environment.py
├── env/                      # world model: data, tasks, reward, state
├── graders/                  # task-specific scoring
├── agent/                    # baseline agent (LLM or heuristic)
├── client.py                 # typed client helper
├── models.py                 # re-exports for importers
├── inference.py              # baseline evaluation driver
├── Dockerfile                # primary image (Spaces / compose)
├── server/Dockerfile         # optional; same recipe, build with `-f server/Dockerfile`
├── docker-compose.yml
├── Makefile
├── .github/workflows/ci.yml  # GitHub Actions (tests + ruff)
├── tests/
├── CONTRIBUTING.md
└── LICENSE
```

## Ship to GitHub

1. **Do not commit build artifacts**: `*.egg-info/`, `dist/`, `.venv/` (see [`.gitignore`](.gitignore)).
2. Initialize or use your remote, then push `main` (or your default branch). CI runs `ruff check` and `pytest` on Python 3.11 and 3.12.
3. In [`pyproject.toml`](pyproject.toml), you can add `[project.urls]` with your repository URL when you create the GitHub repo (optional, helps PyPI metadata later).

## Ship to Hugging Face Spaces

This README includes **YAML frontmatter** at the top for a **Docker** Space (`sdk: docker`, `app_port: 8000`). Typical flow:

1. Create a **Docker** Space and connect it to this Git repository (or push a copy).
2. Ensure the Space build uses the **repository root** [`Dockerfile`](Dockerfile) so `openenv.yaml` and `server.app:app` match the image CMD.
3. **Secrets**: if you use LLM-backed inference inside the Space, add `HF_TOKEN` (or your provider keys) in the Space **Settings → Secrets**, not in the repo.
4. After deploy, health check: `GET /health` on the Space URL.

Hugging Face’s own docs cover Spaces configuration; this project does not duplicate their UI steps.

## LLM configuration (optional)

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-token"
```

## License

See [`LICENSE`](LICENSE).
