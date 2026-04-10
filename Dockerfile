FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY agent /app/agent
COPY env /app/env
COPY graders /app/graders
COPY server /app/server
COPY inference.py app.py client.py models.py __init__.py openenv.yaml /app/

RUN pip install --no-cache-dir ".[openenv]"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "-m", "server.app"]
