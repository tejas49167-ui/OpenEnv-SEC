# Quickstart

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e ".[dev]"
```

## Start The Server

```bash
sec-openenv serve
```

## Smoke Test

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -H 'Content-Type: application/json' -d '{"task":"easy"}'
```

## Run Example Clients

```bash
python examples/clients/async_api_walkthrough.py
python examples/clients/http_api_smoke.py
```

## Run The Baseline Evaluator

```bash
python inference.py
```
