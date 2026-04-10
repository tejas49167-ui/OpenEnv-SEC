# Server

This directory contains the canonical FastAPI application and the environment
entrypoint used by OpenEnv-compatible deployments.

- `app.py` builds the HTTP server
- `cyber_vulnerability_triage_environment.py` exposes the environment class
- `fallback_app.py` keeps the repo runnable without `openenv-core`
- `requirements.txt` mirrors the runtime dependencies used for container builds
