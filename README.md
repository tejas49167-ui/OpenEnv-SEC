---
title: Sec-OpenEnv
emoji: "🕵🏽‍♂️"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: Security-focused environment framework for AI agents
---

# Sec-OpenEnv: Security Execution Environments

A security-focused framework for creating, serving, and evaluating reproducible execution environments for AI agents, inspired by OpenEnv-style contracts and benchmarkable workflows.

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-0f172a)

---

**Featured Environment:** Multi-step application security analysis with deterministic grading in [`cyber-vulnerability-triage`](src/sec_openenv/environments/cyber_vulnerability_triage/).

**Quick Walkthrough:** End-to-end examples for local runs, HTTP API smoke tests, and multi-model evaluation live in [`examples/`](examples/README.md).

## Quick Start

Install the framework locally:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
```

Start a local environment server:

```bash
sec-openenv serve
```

Probe the API:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task":"easy"}'
```

Use the Python API:

```python
from sec_openenv import run_episode

trace = run_episode("cyber-vulnerability-triage", task="hard", seed=2)
print(trace.score)
print(trace.steps)
```

For a more complete walkthrough, check out [docs/quickstart.md](docs/quickstart.md).

## What You Can Run Today

- [Cyber Vulnerability Triage](src/sec_openenv/environments/cyber_vulnerability_triage/): suspicious HTTP request triage with evidence gathering, analyst actions, and deterministic scoring
- [Log Anomaly Investigation](src/sec_openenv/environments/log_anomaly/): operational security workflow for reviewing logs, collecting context, and recommending responses

Each bundled environment includes:

- typed observation and action models
- an environment implementation
- a baseline agent
- a registry entry
- a FastAPI server entrypoint
- evaluation support through the shared framework layer

## Overview

Sec-OpenEnv turns security workflows into reproducible environments for AI agents. It is designed for teams who want something more durable than a one-off benchmark and more structured than a polished demo with hardcoded logic.

The framework keeps the core idea simple: environments should be discoverable, scriptable, testable, and comparable across runs. Instead of evaluating an agent with anecdotal transcripts, you can run the same environment repeatedly with consistent scoring and a stable API surface.

The `sec-openenv` CLI provides commands to list environments, inspect metadata, and serve an environment through FastAPI.

## Architecture

### Component Overview

```text
                         +-----------------------------+
                         |   sec-openenv CLI / API     |
                         | list | info | serve | eval  |
                         +-------------+---------------+
                                       |
                                       v
                         +-----------------------------+
                         |     Environment Registry    |
                         | single source of truth for  |
                         | metadata, entrypoints, app  |
                         +------+------+---------------+
                                |      |
                +---------------+      +------------------+
                |                                      |
                v                                      v
   +-------------------------------+      +-------------------------------+
   | Cyber Vulnerability Triage    |      | Log Anomaly Investigation     |
   | request -> evidence -> action |      | event -> context -> response  |
   +---------------+---------------+      +---------------+---------------+
                   |                                      |
                   +------------------+-------------------+
                                      |
                                      v
                     +-----------------------------------+
                     | FastAPI Serving + Evaluation Loop |
                     | /reset /step /tasks /benchmark    |
                     +-----------------------------------+
```

### Core Components

#### 1. Environment Registry

The registry is the framework control plane. It stores environment metadata, entrypoints, maturity level, and server bindings used by `list`, `info`, and `serve`.

#### 2. Security Environments

Each environment models a real security workflow as a sequence of observations and structured actions. The current bundled environments focus on application-security triage and log-anomaly investigation.

#### 3. FastAPI Serving Layer

Environment servers expose a stable HTTP interface that makes the workflows easy to smoke test, automate, and benchmark from external agents or scripts.

#### 4. Evaluation Utilities

The evaluation layer provides reusable helpers such as `run_episode()` and `evaluate_models()` so you can compare behaviors across prompts, models, or agents without rewriting the benchmark loop.

#### 5. Typed Models

Observations, actions, traces, and metadata use typed Python models so environment behavior is easier to inspect, validate, and extend safely.

## Project Structure

### Framework Layout

```text
src/sec_openenv/
  core/           shared framework contracts and loaders
  framework/      registry and environment discovery
  environments/   bundled security environments
  server/         reusable FastAPI app factory
  evaluation/     run_episode() and multi-model evaluation
  config/         framework configuration helpers

env/              compatibility layer for the original benchmark surface
server/           compatibility server entrypoints
examples/         runnable demos and evaluation scripts
tests/            framework, API, and registry checks
docs/             architecture, quickstart, and extensibility docs
```

### Example Workflows

Use the example scripts to explore the framework:

- [`examples/clients/async_api_walkthrough.py`](examples/clients/async_api_walkthrough.py) for a typed client flow against a local server
- [`examples/clients/http_api_smoke.py`](examples/clients/http_api_smoke.py) for raw HTTP smoke testing
- [`examples/benchmark/run_single_episode.py`](examples/benchmark/run_single_episode.py) for a local benchmark walkthrough without starting the server
- [`examples/evaluate_multiple_models.py`](examples/evaluate_multiple_models.py) for lightweight repeated evaluation runs

## CLI Commands

The `sec-openenv` CLI provides the main entrypoints for interacting with the framework:

- `sec-openenv list` lists bundled environments
- `sec-openenv info --environment cyber-vulnerability-triage` prints registry and metadata details
- `sec-openenv serve --environment cyber-vulnerability-triage --port 8000` runs a local FastAPI server

### Quick CLI Usage

```bash
sec-openenv list
sec-openenv info --environment cyber-vulnerability-triage
sec-openenv serve --environment cyber-vulnerability-triage --port 8000
sec-openenv serve --environment log-anomaly --port 8001
```

## Python API

The package also exposes a simple programmatic surface:

```python
from sec_openenv import evaluate_models, list_environments, run_episode

print([env.slug for env in list_environments()])

trace = run_episode("cyber-vulnerability-triage", task="hard", seed=2)
print(trace.score, trace.steps)

results = evaluate_models(
    "cyber-vulnerability-triage",
    ["gpt-4o-mini", "gpt-4.1-mini"],
    task="hard",
    episodes=2,
)
print(results)
```

## Design Principles

1. **Reproducibility**: security workflows should be rerunnable, inspectable, and benchmarkable
2. **Registry-Driven Discovery**: environments should be surfaced through one consistent framework contract
3. **Deterministic Evaluation**: scoring should make model and prompt comparisons meaningful
4. **Practical Serving**: environments should be easy to expose through a scriptable HTTP interface
5. **Extensibility**: new security domains should fit into the same framework without rewriting the core

## Development

### Installation

```bash
git clone https://github.com/tejas/sec-openenv.git
cd sec-openenv
python -m pip install -e ".[dev]"
```

Optional OpenAI-compatible dependencies for LLM-backed evaluation:

```bash
python -m pip install -e ".[llm]"
```

### Running Tests

```bash
pytest
```

### Running Examples

```bash
python examples/clients/async_api_walkthrough.py
python examples/clients/http_api_smoke.py
python examples/benchmark/run_single_episode.py
python examples/evaluate_multiple_models.py
```

## Extending The Framework

To add a new environment:

1. Create a package under `src/sec_openenv/environments/<your_env>/`.
2. Add typed models, an environment class, a baseline agent, and a server module.
3. Register it in [`src/sec_openenv/framework/registry.py`](src/sec_openenv/framework/registry.py).
4. Add an example and at least one framework or API test.

The registry is the single source of truth for what counts as part of the framework surface.

## Docs

- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [Environments](docs/environments.md)
- [Extensibility](docs/extensibility.md)
- [Security Model](docs/security-model.md)
- [Roadmap](docs/roadmap.md)

## Validation

```bash
pytest
```
