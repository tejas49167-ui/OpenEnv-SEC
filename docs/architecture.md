# Architecture

Sec-OpenEnv is organized as a small but scalable framework for security environments. The repository currently ships one environment, but the layout is meant to support multiple environments, shared tooling, and future ecosystem growth.

## Design Goals

- Preserve the existing cyber triage benchmark logic exactly.
- Present the repository as a framework others can build on.
- Separate benchmark internals from framework-facing surfaces.
- Keep extension paths obvious without unnecessary abstraction.

## Layer Model

### Framework Layer

Located under `src/sec_openenv/`.

Responsibilities:

- top-level package identity
- version metadata
- CLI entrypoint
- environment registry
- configuration helpers

### Environment Layer

The current environment implementation remains in `env/`.

Responsibilities:

- deterministic example loading
- task definitions
- observation and action models
- reward calculation
- state transitions

### Runtime Layer

Located under `server/`.

Responsibilities:

- FastAPI app creation
- OpenEnv integration when available
- fallback HTTP server support
- browser-friendly landing page

### Ecosystem Layer

Cross-cutting project surfaces:

- `examples/`
- `docs/`
- `rfcs/`
- `.github/`
- `configs/`
- `tests/`

## Current Component Relationships

```text
sec_openenv.cli
  -> sec_openenv.framework.registry
  -> server.app

server.app / server.fallback_app
  -> env.environment
  -> env.models
  -> env.tasks

client.py
  -> env.models
  -> OpenEnv client types when installed

inference.py
  -> agent.baseline_agent
  -> env.environment
```

## Why The Compatibility Layer Exists

Existing usage already points at `cyber_vulnerability_triage`, `server.app`, `client.py`, and `models.py`.

To avoid breaking users while improving structure, the repository now exposes:

- a canonical framework namespace: `sec_openenv`
- a compatibility package: `cyber_vulnerability_triage`
- the existing runtime modules for legacy commands and scripts
