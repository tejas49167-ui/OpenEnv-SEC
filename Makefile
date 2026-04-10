.PHONY: help venv install dev server test lint format docker-build docker-run clean

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
	@echo "  test         Run tests"
	@echo "  lint         Run ruff lint"
	@echo "  format       Run ruff format"
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

test:
	$(PYTEST)

lint:
	$(RUFF) check .

format:
	$(RUFF) format .

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
