# Extensibility

Sec-OpenEnv is intentionally set up to grow into a multi-environment ecosystem.

## What Can Be Extended

- additional security environments
- benchmark reporting and analysis tools
- environment packaging metadata
- server adapters and deployment recipes
- environment-authoring documentation

## Adding A New Environment

1. Create a new package under `src/sec_openenv/environments/<environment_name>/`.
2. Implement the environment logic with typed models and deterministic tasks where possible.
3. Add a server entrypoint that supports the existing API contract.
4. Register the environment in `src/sec_openenv/framework/registry.py`.
5. Add examples in `examples/`.
6. Add tests for environment logic and HTTP behavior.
7. Document it in `docs/` and, if the design is substantial, add an RFC.

## Extension Principles

- Prefer explicit modules over plugin magic.
- Preserve stable import and runtime contracts.
- Keep environment logic understandable end to end.
- Avoid abstraction layers that only serve one environment.
