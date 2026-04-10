from __future__ import annotations


def render_landing_page() -> str:
    return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Cyber Vulnerability Triage</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f6f7f2;
        --panel: #fffdfa;
        --ink: #1b1f18;
        --muted: #5b6555;
        --accent: #0f766e;
        --accent-2: #d97706;
        --border: #d8ddcf;
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        font-family: "Segoe UI", "Helvetica Neue", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(217, 119, 6, 0.12), transparent 28%),
          radial-gradient(circle at top right, rgba(15, 118, 110, 0.14), transparent 32%),
          var(--bg);
        color: var(--ink);
      }

      main {
        max-width: 920px;
        margin: 0 auto;
        padding: 48px 20px 64px;
      }

      .hero,
      .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 20px;
        box-shadow: 0 18px 50px rgba(27, 31, 24, 0.08);
      }

      .hero {
        padding: 32px;
        margin-bottom: 20px;
      }

      .eyebrow {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(15, 118, 110, 0.09);
        color: var(--accent);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      h1 {
        margin: 16px 0 10px;
        font-size: clamp(2rem, 5vw, 3.4rem);
        line-height: 1.05;
      }

      p {
        margin: 0;
        color: var(--muted);
        line-height: 1.6;
        font-size: 1.02rem;
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
      }

      .button {
        text-decoration: none;
        padding: 12px 16px;
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid var(--border);
      }

      .button.primary {
        background: var(--accent);
        color: white;
        border-color: var(--accent);
      }

      .button.secondary {
        background: white;
        color: var(--ink);
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
      }

      .card {
        padding: 20px;
      }

      .card h2 {
        margin: 0 0 12px;
        font-size: 1.05rem;
      }

      ul {
        margin: 0;
        padding-left: 18px;
        color: var(--muted);
        line-height: 1.7;
      }

      code {
        font-family: "SFMono-Regular", Consolas, monospace;
        font-size: 0.95em;
        color: var(--accent-2);
      }

      @media (max-width: 640px) {
        .hero { padding: 24px; }
        main { padding-top: 28px; }
      }
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <span class="eyebrow">OpenEnv API</span>
        <h1>Cyber Vulnerability Triage</h1>
        <p>
          This deployment is an API-first benchmark for application security alert triage.
          Use the links below to inspect health, metadata, tasks, and benchmark endpoints.
        </p>
        <div class="actions">
          <a class="button primary" href="/docs">Open API Docs</a>
          <a class="button secondary" href="/health">Health Check</a>
          <a class="button secondary" href="/benchmark">Benchmark Info</a>
        </div>
      </section>

      <section class="grid">
        <article class="card">
          <h2>Core Endpoints</h2>
          <ul>
            <li><code>GET /health</code></li>
            <li><code>GET /metadata</code></li>
            <li><code>GET /tasks</code></li>
            <li><code>GET /benchmark</code></li>
          </ul>
        </article>

        <article class="card">
          <h2>Session Actions</h2>
          <ul>
            <li><code>POST /reset</code></li>
            <li><code>POST /step</code></li>
            <li><code>GET /state</code></li>
          </ul>
        </article>

        <article class="card">
          <h2>What You’re Seeing</h2>
          <ul>
            <li>The homepage is HTML for browsers.</li>
            <li>The benchmark routes still return JSON.</li>
            <li><code>/docs</code> provides the interactive FastAPI UI.</li>
          </ul>
        </article>
      </section>
    </main>
  </body>
</html>
"""
