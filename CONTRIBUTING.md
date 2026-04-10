# Contributing

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
```

Or:

```bash
make venv
make dev
```

## Quality checks

```bash
make test
make lint
make format
```

## Pull request guidelines

- Keep changes focused and well-tested.
- If you change environment behavior, update or add tests in `tests/`.
- If you change API shapes, update `README.md` examples.

## Before you commit (GitHub / Hugging Face)

- Never commit `*.egg-info/`, `__pycache__/`, or `.venv/`—they are listed in `.gitignore`.
- Run `make test` (or `pytest`) and `make lint` after substantive edits.
- For Hugging Face Spaces, keep secrets (tokens) in Space settings, not in the repository.
