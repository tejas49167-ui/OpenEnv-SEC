# Optional alternate build context (OpenEnv envs often keep a server-local Dockerfile).
# The canonical image for this repo is the Dockerfile at the repository root (Hugging Face / docker compose).
#
# Build from repo root:
#   docker build -f server/Dockerfile .
#
# Same runtime as root Dockerfile; kept for symmetry with OpenEnv `envs/*/server/Dockerfile` layouts.

FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE MANIFEST.in /app/
COPY src /app/src
COPY agent /app/agent
COPY env /app/env
COPY graders /app/graders
COPY server /app/server
COPY configs /app/configs
COPY inference.py app.py client.py models.py __init__.py openenv.yaml /app/

RUN pip install --no-cache-dir ".[openenv]"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
