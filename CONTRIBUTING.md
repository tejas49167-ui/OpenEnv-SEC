# Contributing

Thanks for contributing to Sec-OpenEnv.

This repository is maintained as a **security environment framework**. Contributions should make the project easier to adopt, extend, benchmark, and trust without changing the core meaning of the environments it ships.

## Project Principles

- Preserve the existing benchmark concepts and task semantics.
- Prefer deterministic behavior for environments, grading, and tests.
- Optimize for clarity, portability, and realistic extensibility.
- Treat docs, examples, and packaging as first-class project surfaces.

## Repository Map

- `src/sec_openenv/`: framework namespace, registry, and CLI
- `src/cyber_vulnerability_triage/`: compatibility package for existing imports
- `env/`: current benchmark implementation internals
- `server/`: FastAPI server entrypoints
- `examples/`: runnable client and benchmark examples
- `docs/`: architecture, environments, extensibility, security, roadmap
- `rfcs/`: larger future-facing design proposals
- `tests/`: API and environment contract coverage

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
```

## Daily Commands

```bash
make test
make lint
make format
make server
make docs
python inference.py
sec-openenv list
```

## Recommended Contribution Flow

1. Open an issue for bug fixes that affect behavior or for proposals that add new surfaces.
2. For larger design changes, add an RFC in `rfcs/` before implementation.
3. Keep changes focused and document any user-facing impact.
4. Add or update tests for behavior changes.
5. Run linting and the relevant test subset before opening a pull request.

## Pull Request Expectations

- Keep PRs reviewable and scoped around one concern.
- Include a short rationale and a validation section.
- Update `README.md`, `docs/`, or examples when developer workflows change.
- Preserve backward compatibility where practical for existing imports and commands.
- Do not introduce nondeterministic benchmark behavior without a clear justification.

## Adding A New Environment

1. Create a new package under `src/sec_openenv/environments/`.
2. Implement the environment logic with typed models and deterministic tasks where possible.
3. Add a server entrypoint that supports the existing API contract.
4. Register the environment in `src/sec_openenv/framework/registry.py`.
5. Add examples in `examples/`.
6. Add tests for environment logic and HTTP behavior.
7. Document it in `docs/` and, if the design is substantial, add an RFC.

See [docs/extensibility.md](docs/extensibility.md) for the detailed checklist.

## Before Opening A PR

- Run `make test`
- Run `make lint`
- Run `make format`
- Make sure the server starts locally
- Verify examples still reflect the current public API
- Check that secrets or personal tokens are not in the diff

## Good First Contributions

- improve examples and quickstart flows
- expand tests around the API contract
- refine documentation and architecture notes
- strengthen packaging, release, or CI metadata
- add contributor tooling for environment authors
