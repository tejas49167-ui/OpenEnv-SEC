from __future__ import annotations

import os
from typing import Literal, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from env.environment import CyberVulnerabilityTriageEnvironment
from env.models import TASK_LABELS
from env.models import Action


class ResetRequest(BaseModel):
    task: Optional[Literal["easy", "medium", "hard"]] = None


app = FastAPI(title="Cybersecurity Alert Triage OpenEnv", version="2.0.0")
environment = CyberVulnerabilityTriageEnvironment()


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    tasks = "".join(
        f"<li><strong>{task_id}</strong>: {TASK_LABELS[task_id]}</li>"
        for task_id in ["easy", "medium", "hard"]
    )
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Cybersecurity Alert Triage OpenEnv</title>
        <style>
          :root {{
            color-scheme: light;
            --bg: #0f172a;
            --panel: #111827;
            --muted: #cbd5e1;
            --text: #f8fafc;
            --accent: #f97316;
            --accent-2: #22c55e;
          }}
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            font-family: ui-sans-serif, system-ui, sans-serif;
            background:
              radial-gradient(circle at top, rgba(249, 115, 22, 0.24), transparent 35%),
              linear-gradient(135deg, #020617, var(--bg));
            color: var(--text);
          }}
          .wrap {{
            max-width: 920px;
            margin: 0 auto;
            padding: 48px 20px 64px;
          }}
          .panel {{
            background: rgba(17, 24, 39, 0.88);
            border: 1px solid rgba(203, 213, 225, 0.14);
            border-radius: 20px;
            padding: 28px;
            backdrop-filter: blur(8px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
          }}
          .eyebrow {{
            display: inline-block;
            margin-bottom: 12px;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.15);
            color: #bbf7d0;
            font-size: 14px;
          }}
          h1 {{
            margin: 0 0 12px;
            font-size: clamp(32px, 6vw, 52px);
            line-height: 1.05;
          }}
          p {{
            color: var(--muted);
            font-size: 17px;
            line-height: 1.6;
          }}
          ul {{
            padding-left: 20px;
            line-height: 1.8;
            color: var(--muted);
          }}
          .actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 24px;
          }}
          a {{
            color: inherit;
            text-decoration: none;
          }}
          .button {{
            display: inline-block;
            padding: 12px 16px;
            border-radius: 12px;
            font-weight: 600;
          }}
          .button.primary {{
            background: var(--accent);
            color: white;
          }}
          .button.secondary {{
            border: 1px solid rgba(203, 213, 225, 0.18);
            background: rgba(255, 255, 255, 0.03);
          }}
          code {{
            background: rgba(255, 255, 255, 0.08);
            padding: 2px 6px;
            border-radius: 6px;
          }}
        </style>
      </head>
      <body>
        <main class="wrap">
          <section class="panel">
            <div class="eyebrow">OpenEnv Security Lab</div>
            <h1>Cybersecurity Alert Triage Environment</h1>
            <p>
              This Space hosts a FastAPI-backed OpenEnv environment for practicing
              analyst-style investigation of suspicious HTTP requests.
            </p>
            <p>Available tasks:</p>
            <ul>{tasks}</ul>
            <p>
              API endpoints: <code>GET /health</code>, <code>POST /reset</code>,
              <code>POST /step</code>, and <code>GET /state</code>.
            </p>
            <div class="actions">
              <a class="button primary" href="/docs">Open API Docs</a>
              <a class="button secondary" href="/health">Health Check</a>
            </div>
          </section>
        </main>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None) -> dict:
    observation = environment.reset(request.task if request else None)
    return observation.model_dump()


@app.post("/step")
def step(action: Action) -> dict:
    observation, reward, done, info = environment.step(action)
    return {
        "observation": observation.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def state() -> dict:
    return environment.state().model_dump()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
