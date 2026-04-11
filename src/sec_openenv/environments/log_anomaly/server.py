from __future__ import annotations

import os

import uvicorn

from sec_openenv.server.factory import create_environment_app

app = create_environment_app("log-anomaly")


def main() -> None:
    port = int(os.getenv("API_PORT", os.getenv("PORT", "8002")))
    uvicorn.run(app, host="0.0.0.0", port=port)
