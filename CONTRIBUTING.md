# Contributing

Sec-OpenEnv is maintained as a security environment framework. Good contributions improve the framework surface, preserve determinism, and make the project easier to trust and extend.

## Contributor Onboarding

```bash
git clone https://github.com/tejas/sec-openenv.git
cd sec-openenv
python -m pip install -e .
python -m pip install pytest ruff
pytest
sec-openenv list
```

## Design Principles

- Keep the core idea intact: security workflows should become reproducible environments for AI agents.
- Preserve compatibility where reasonable for the original cyber triage surface.
- Prefer registry-driven behavior over hardcoded environment wiring.
- Keep datasets, evaluation, docs, and packaging first-class.
- Make environments deterministic unless nondeterminism is the feature being tested.

## Where Things Go

- `src/sec_openenv/core/`: shared framework primitives
- `src/sec_openenv/framework/`: registry and discovery
- `src/sec_openenv/environments/`: canonical packaged environments
- `src/sec_openenv/server/`: reusable server factory
- `src/sec_openenv/evaluation/`: shared episode and model evaluation helpers
- `env/` and `server/`: compatibility shims for legacy imports
- `examples/`: runnable demos
- `tests/`: contract and regression coverage

## Adding A New Environment

1. Create `src/sec_openenv/environments/<env_name>/`.
2. Add a dataset, typed models, environment class, baseline agent, and server module.
3. Register it in `src/sec_openenv/framework/registry.py`.
4. Add one runnable example and at least one smoke test.
5. Update the README or docs if the environment is user-facing.

If the change introduces a new framework pattern, add an RFC in `rfcs/`.

## Pull Request Checklist

- Run `pytest`
- Run `ruff check .`
- Verify `sec-openenv list` and `sec-openenv info --environment <env>` still work
- Update examples or docs when user-facing behavior changes
- Avoid breaking the original cyber triage workflow unless the change is intentional and documented

## Review Expectations

- Keep PRs scoped
- explain why the change improves the framework
- include validation notes
- call out compatibility implications explicitly

## Good First Issues

- new smoke tests
- small environment expansions
- docs and example improvements
- CI or packaging polish
- contributor ergonomics for environment authors
