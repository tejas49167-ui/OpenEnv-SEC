<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

=======
# ---------- Builder stage ----------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

>>>>>>> cstech
COPY pyproject.toml README.md LICENSE MANIFEST.in /app/
COPY src /app/src
COPY agent /app/agent
COPY env /app/env
COPY graders /app/graders
COPY server /app/server
COPY configs /app/configs
COPY inference.py app.py client.py models.py __init__.py openenv.yaml /app/

<<<<<<< HEAD
RUN pip install --no-cache-dir ".[openenv]"
=======

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[openenv]"


# ---------- Final stage ----------
FROM python:3.11-slim

WORKDIR /app


COPY --from=builder /opt/venv /opt/venv


COPY --from=builder /app /app


ENV PATH="/opt/venv/bin:$PATH"
>>>>>>> cstech

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

<<<<<<< HEAD
CMD ["python", "-m", "server.app"]
=======
CMD ["python", "-m", "server.app"]
>>>>>>> cstech
