# Quickstart

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
```

## Run the server

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

## Run the baseline

```bash
python inference.py
```

## Try the typed client

```bash
python examples/local_cyber_triage.py
```
