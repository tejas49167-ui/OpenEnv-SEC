from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from sec_openenv.framework.registry import get_environment


class ResetRequest(BaseModel):
    task: str | None = None
    seed: int | None = None
    case_index: int | None = None


def render_environment_page(info: dict[str, Any]) -> str:
    tasks_html = "".join(
        f"<li><strong>{task.get('id', task.get('name', 'task'))}</strong>: {task['description']}</li>"
        for task in info["tasks"]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{info["display_name"]}</title>
    <style>
      :root {{
        --bg: #f4efe4;
        --panel: #fffdfa;
        --ink: #1c1814;
        --muted: #645d56;
        --accent: #0f766e;
        --accent-2: #b45309;
        --border: #ddd0bf;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Segoe UI", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(180, 83, 9, 0.13), transparent 28%),
          radial-gradient(circle at top right, rgba(15, 118, 110, 0.15), transparent 32%),
          var(--bg);
      }}
      main {{ max-width: 960px; margin: 0 auto; padding: 48px 20px 64px; }}
      .hero, .card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 20px;
        box-shadow: 0 18px 40px rgba(28, 24, 20, 0.08);
      }}
      .hero {{ padding: 32px; margin-bottom: 18px; }}
      .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
      .card {{ padding: 20px; }}
      .eyebrow {{
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: rgba(15, 118, 110, 0.1); color: var(--accent); font-size: 12px;
        font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
      }}
      h1 {{ margin: 14px 0 10px; font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.04; }}
      p, li {{ color: var(--muted); line-height: 1.6; }}
      a.button {{
        display: inline-block; margin-right: 10px; margin-top: 20px; padding: 12px 16px;
        border-radius: 12px; background: var(--accent); color: white; text-decoration: none;
      }}
      code {{ color: var(--accent-2); }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <span class="eyebrow">Sec-OpenEnv Environment</span>
        <h1>{info["display_name"]}</h1>
        <p>{info["description"]}</p>
        <a class="button" href="/docs">Open API Docs</a>
        <a class="button" href="/benchmark">Benchmark Info</a>
      </section>
      <section class="grid">
        <article class="card">
          <h2>Domain</h2>
          <p>{info["domain"]}</p>
        </article>
        <article class="card">
          <h2>Tasks</h2>
          <ul>{tasks_html}</ul>
        </article>
        <article class="card">
          <h2>Endpoints</h2>
          <p><code>GET /health</code>, <code>GET /benchmark</code>, <code>POST /reset</code>, <code>POST /step</code></p>
        </article>
      </section>
    </main>
  </body>
</html>"""


def create_environment_app(environment_slug: str) -> FastAPI:
    descriptor = get_environment(environment_slug)
    environment = descriptor.create_environment()
    action_model = descriptor.load_action_model()
    metadata = environment.get_metadata()
    if hasattr(metadata, "model_dump"):
        metadata_payload = metadata.model_dump()
    elif is_dataclass(metadata):
        metadata_payload = asdict(metadata)
    else:
        metadata_payload = dict(metadata)

    app = FastAPI(title=metadata_payload["name"], version=metadata_payload.get("version", "0.1.0"))

    def benchmark_info() -> dict[str, Any]:
        return {
            "name": descriptor.slug,
            "display_name": descriptor.display_name,
            "domain": descriptor.domain,
            "description": descriptor.description,
            "episodes": len(getattr(environment, "examples", [])),
            "tasks": [
                {"id": task.name, **task.to_dict()} for task in environment.task_catalog.values()
            ],
            "primary_entrypoint": descriptor.server_entrypoint,
            "supports_concurrent_sessions": getattr(
                environment, "supports_concurrent_sessions", False
            ),
            "maturity": descriptor.maturity,
        }

    def list_tasks() -> dict[str, Any]:
        return {
            "tasks": [
                {"id": task.name, **task.to_dict()} for task in environment.task_catalog.values()
            ]
        }

    def root() -> str:
        return render_environment_page(benchmark_info())

    def health() -> dict[str, str]:
        return {"status": "healthy"}

    @app.get("/", response_class=HTMLResponse)
    def root_route() -> str:
        return root()

    @app.get("/health")
    def health_route() -> dict[str, str]:
        return health()

    @app.get("/metadata")
    def metadata_route() -> dict[str, Any]:
        return metadata_payload

    @app.get("/tasks")
    def tasks_route() -> dict[str, Any]:
        return list_tasks()

    @app.get("/benchmark")
    def benchmark_route() -> dict[str, Any]:
        return benchmark_info()

    @app.post("/reset")
    def reset_route(request: ResetRequest | None = None) -> dict[str, Any]:
        observation = environment.reset(
            task=request.task if request else None,
            seed=request.seed if request else None,
            case_index=request.case_index if request else None,
        )
        return {
            "observation": observation.model_dump(),
            "reward": observation.reward,
            "done": observation.done,
        }

    @app.post("/step")
    async def step_route(request: Request) -> dict[str, Any]:
        body = await request.json()
        action = action_model.model_validate(body)
        observation = environment.step(action)
        return {
            "observation": observation.model_dump(),
            "reward": observation.reward,
            "done": observation.done,
            "info": observation.metadata.get("info", {}),
        }

    @app.get("/state")
    def state_route() -> dict[str, Any]:
        return environment.state.model_dump()

    app.state.environment_slug = environment_slug
    app.state.benchmark_info = benchmark_info
    app.state.list_tasks = list_tasks
    app.state.root_handler = root
    app.state.health_handler = health
    return app
