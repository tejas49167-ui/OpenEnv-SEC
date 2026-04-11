---
title: Sec-OpenEnv
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: Security benchmark framework for cyber triage
---

<img width="40" height="40" alt="Sec-OpenEnv logo" src="assets/logo.svg" /> **Sec-OpenEnv**

![Install](https://img.shields.io/badge/install-pip%20install%20--e%20.-1f6feb)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![FastAPI](https://img.shields.io/badge/api-FastAPI-009688)
![License](https://img.shields.io/badge/license-MIT-0f172a)
![OpenEnv](https://img.shields.io/badge/OpenEnv-compatible-475569)
![Status](https://img.shields.io/badge/maturity-beta-b45309)

Sec-OpenEnv is a **security environment framework** for building, serving, and evaluating structured security workflows. This repository currently ships one complete environment, **Cyber Vulnerability Triage**, and is organized so future environments, plugins, benchmarks, and training loops can grow around the same contract.

The benchmark itself is unchanged: an agent receives a suspicious web request, investigates through structured actions, and submits a final triage decision with deterministic grading. What changes here is the repository maturity around that benchmark: packaging, documentation, extensibility, examples, and contributor experience.

## Problem

Most security-eval repos are either:

- toy classification datasets with no workflow realism
- custom demos that are hard to install, extend, compare, or benchmark

Sec-OpenEnv fills the gap with a framework-shaped repository for **multi-step security reasoning**.

## Why This Matters

Security operations are not one-shot labels. Real triage involves context gathering, selective investigation, and operationally safe decisions. Sec-OpenEnv makes that workflow reproducible enough for research and structured enough for industry experimentation.

## Architecture

```text
                    +-----------------------------------+
                    |           Sec-OpenEnv             |
                    |  framework metadata + CLI + docs  |
                    +-------------------+---------------+
                                        |
                                        v
                +---------------------------------------------+
                | Environment Module: Cyber Vulnerability     |
                | Triage                                      |
                |                                             |
                |  Actions -> State -> Reward                 |
                |  inspect_payload                            |
                |  decode_obfuscation                         |
                |  review_history                             |
                |  check_source_reputation                    |
                |  inspect_asset_context                      |
                |  consult_playbook                           |
                |  submit_triage                              |
                +-------------------+-------------------------+
                                    |
               +--------------------+--------------------+
               |                                         |
               v                                         v
     +-----------------------+                 +-----------------------+
     | Deterministic Dataset |                 | FastAPI / OpenEnv API |
     | env/data.py           |                 | /reset /step /state   |
     | env/tasks.py          |                 | /metadata /health     |
     +-----------------------+                 +-----------------------+
                                    |
                                    v
                      +------------------------------+
                      | Benchmarking / Evaluation    |
                      | baseline agent + inference   |
                      | examples + external tooling  |
                      +------------------------------+
```

## Key Features

- **Framework-style layout** with `src/sec_openenv/` for scalable growth
- **Deterministic security environment** for reproducible evaluation
- **OpenEnv-compatible API** for local, Docker, and hosted deployment
- **Contributor-ready docs** covering architecture, extensibility, security, and roadmap
- **Compatibility-preserving structure** so the existing benchmark logic remains intact

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
sec-openenv serve
```

Smoke test:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset \
  -H 'Content-Type: application/json' \
  -d '{"task":"hard"}'
```

Run a realistic example:

```bash
python examples/clients/async_api_walkthrough.py
```

Run the baseline benchmark:

```bash
python inference.py
```

## Example Usage

```python
import asyncio

from cyber_vulnerability_triage import CyberVulnerabilityTriageEnv


async def main() -> None:
    async with CyberVulnerabilityTriageEnv(base_url="http://localhost:8000") as env:
        result = await env.reset(task="hard")
        print(result.observation.request_id)

        await env.inspect_payload()
        await env.review_history()

        final = await env.submit_triage(
            vulnerability_type="xss",
            severity="medium",
            response_action="sanitize",
            explanation="Payload and context indicate reflected script injection.",
        )
        print(final.done, final.reward)


asyncio.run(main())
```

## Real Usage Flows

- **Researcher benchmark run**: start the server, run `python inference.py`, compare `easy`, `medium`, and `hard`.
- **Platform demo**: deploy the FastAPI server, connect a client, replay deterministic cases for demos.
- **Environment authoring**: add new modules under `src/sec_openenv/environments/`, register them, and document them.

## Why This Is Different

- It treats a security benchmark like a **framework module**, not a script dump.
- It is designed for **experimentation, benchmarking, and training** from the same foundation.
- It includes the ecosystem signals maintainers, researchers, and adopters look for before taking a project seriously.

## Repository Structure

```text
.
├── src/
│   ├── sec_openenv/
│   │   ├── cli.py
│   │   ├── core/
│   │   ├── framework/
│   │   ├── config/
│   │   └── environments/
│   │       └── cyber_vulnerability_triage/
│   └── cyber_vulnerability_triage/
│       └── server/
├── env/
├── graders/
├── server/
├── examples/
├── docs/
├── rfcs/
├── configs/
├── tests/
└── assets/
```

## Documentation Map

- [docs/architecture.md](docs/architecture.md)
- [docs/environments.md](docs/environments.md)
- [docs/extensibility.md](docs/extensibility.md)
- [docs/security-model.md](docs/security-model.md)
- [docs/roadmap.md](docs/roadmap.md)
- [rfcs/0001-environment-registry.md](rfcs/0001-environment-registry.md)
- [rfcs/0002-evaluation-traces.md](rfcs/0002-evaluation-traces.md)

## Screenshots And Demo Placeholders

- `docs/assets/server-home.png`
- `docs/assets/openapi-docs.png`
- `docs/assets/benchmark-run.png`

## Ecosystem Signals

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [ROADMAP.md](ROADMAP.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
- [.env.example](.env.example)
- [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [.github/pull_request_template.md](.github/pull_request_template.md)

## Contributor Call To Action

High-impact contributions include:

- new security environments
- stronger eval tooling
- more deterministic cases and tests
- better docs, demos, and deployment recipes

Start with [CONTRIBUTING.md](CONTRIBUTING.md), and use `rfcs/` for bigger design ideas.
