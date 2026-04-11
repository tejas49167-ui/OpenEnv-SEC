# Changelog

All notable changes to this project should be documented in this file.

## [Unreleased]

### Added

- optional dependency group `llm` (`openai`) for LLM-backed evaluation; core install stays lightweight
- HTTP contract tests for all registry environments via `TestClient`
- CI: Ruff format check, pytest coverage gate, wheel/sdist build verification, Docker image smoke test
- `httpx` in dev extras for FastAPI test client
- `MANIFEST.in` includes `docs/assets` (SVG, JSON) for complete sdists

### Changed

- Docker images run `sec-openenv serve` with `PORT` respected (`${PORT:-8000}`)
- `POST /step` on registry apps parses JSON with the environment action model explicitly (fixes FastAPI treating dynamic `Action` types as query params)
- `evaluate_models` builds an OpenAI client only when `openai` is installed and credentials are set

### Fixed

- `build_openai_client()` handles missing `openai` package without import errors

## [2.1.0] - 2026-04-11

### Added

- registry-driven serving and metadata flow
- two new bundled environments: `phishing-detection` and `log-anomaly-response`
- reusable evaluation helpers: `run_episode()` and `evaluate_models()`
- `examples/evaluate_multiple_models.py`
- CI workflow for install, lint, and tests
- docs assets for architecture, CLI output, and API examples

### Changed

- promoted `src/sec_openenv/` to the canonical framework surface
- expanded the cyber vulnerability triage dataset from the original small seed set to 48 generated cases
- rewired the CLI to use the registry as the single source of truth
- refreshed packaging and compatibility shims around the original benchmark surface
- rewrote top-level docs to position the project as a security-focused framework inspired by OpenEnv principles

### Preserved

- the core cyber vulnerability triage workflow and behavior
- the original compatibility import surfaces for the existing environment and server paths
