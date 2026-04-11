.PHONY: help venv install dev server framework-server test lint format docs smoke docker-build docker-run clean

VENV ?= .venv
PY ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip
RUFF ?= $(VENV)/bin/ruff
PYTEST ?= $(VENV)/bin/pytest

help:
	@echo "Targets:"
	@echo "  venv         Create .venv"
	@echo "  install      Install package"
	@echo "  dev          Install dev extras"
	@echo "  server       Run API server"
	@echo "  framework-server Run API server through sec-openenv CLI"
	@echo "  test         Run tests"
	@echo "  lint         Run ruff lint"
	@echo "  format       Run ruff format"
	@echo "  docs         Build docs"
	@echo "  smoke        Run health and reset smoke checks"
	@echo "  docker-build Build docker image"
	@echo "  docker-run   Run docker image (API)"
	@echo "  clean        Remove __pycache__, *.pyc, local caches (safe before git commit)"

venv:
	python -m venv $(VENV)
	$(PIP) install -U pip setuptools wheel

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev]"

server:
	$(PY) -m uvicorn server.app:app --host 0.0.0.0 --port 8000

framework-server:
	$(PY) -m sec_openenv.cli serve

test:
	$(PYTEST)

lint:
	$(RUFF) check .

format:
	$(RUFF) format .

docs:
	make -C docs html

smoke:
	curl -fsS http://localhost:8000/health
	curl -fsS -X POST http://localhost:8000/reset -H 'Content-Type: application/json' -d '{"task":"easy"}'

docker-build:
	docker build -t cyber-openenv .

docker-run:
	docker run --rm -p 8000:8000 cyber-openenv

# Remove generated Python/cache artifacts (does not delete .venv)
clean:
	find . -type d -name __pycache__ | while IFS= read -r d; do rm -rf "$$d"; done
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	rm -rf *.egg-info
