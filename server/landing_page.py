from __future__ import annotations

<<<<<<< HEAD
import json


def render_landing_page(base_path: str = "") -> str:
    return (
        """<!DOCTYPE html>
=======

def render_landing_page() -> str:
    return """<!DOCTYPE html>
>>>>>>> cstech
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Cyber Vulnerability Triage</title>
    <style>
      :root {
<<<<<<< HEAD
        color-scheme: dark;
        --bg: #0d1017;
        --panel: #0f131b;
        --surface: #11161f;
        --surface-2: #2a2f38;
        --border: #303743;
        --border-strong: #c8ccd4;
        --text: #f4f6fa;
        --muted: #9aa3b2;
=======
        color-scheme: light;
        --bg: #f6f7f2;
        --panel: #fffdfa;
        --ink: #1b1f18;
        --muted: #5b6555;
        --accent: #0f766e;
        --accent-2: #d97706;
        --border: #d8ddcf;
>>>>>>> cstech
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
<<<<<<< HEAD
        background: var(--bg);
        color: var(--text);
        font-family: "Segoe UI", sans-serif;
      }

      main {
        width: min(1174px, calc(100% - 34px));
        margin: 0 auto;
        padding: 34px 0 28px;
      }

      .layout {
        display: grid;
        grid-template-columns: 386px 1fr;
        gap: 30px;
        align-items: start;
      }

      .sidebar {
        padding-top: 10px;
      }

      .sidebar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
      }

      .sidebar-header h2 {
        margin: 0;
        font-size: 1.18rem;
        font-weight: 500;
      }

      .caret {
        color: var(--text);
        font-size: 0.88rem;
      }

      .sidebar-section {
        margin-bottom: 22px;
      }

      .sidebar-title {
        margin: 0 0 10px;
        font-size: 0.92rem;
        color: var(--text);
        font-weight: 600;
      }

      .sidebar-copy {
        margin: 0 0 12px;
        color: var(--text);
        font-size: 0.98rem;
        line-height: 1.5;
      }

      .sidebar-subtitle {
        margin: 0 0 8px;
        font-size: 0.92rem;
        color: var(--text);
        font-weight: 400;
        line-height: 1.45;
      }

      .meta-links {
        display: flex;
        gap: 10px;
        margin-top: 10px;
      }

      .meta-links a {
        color: var(--muted);
        font-size: 0.66rem;
        text-decoration: none;
      }

      .inline-code {
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid var(--border);
        background: #171c25;
        font-family: Consolas, monospace;
        font-size: 0.9em;
      }

      .py-keyword { color: #c678dd; }
      .py-name { color: #e7ebf3; }
      .py-class { color: #e5c07b; }
      .py-string { color: #98c379; }
      .py-func { color: #61afef; }
      .py-op { color: #cfd6e4; }

      .code-card {
        position: relative;
        border: 1px solid var(--border);
        background: #3a414d;
        overflow: hidden;
      }

      .code-card pre {
        margin: 0;
        padding: 15px 14px 17px;
        overflow: auto;
        color: #e7ebf3;
        font-family: Consolas, monospace;
        font-size: 0.84rem;
        line-height: 1.5;
        white-space: pre;
      }

      .copy-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        color: #d6dae1;
        font-size: 0.85rem;
      }

      .scrollbar {
        height: 13px;
        background: #ececec;
        position: relative;
      }

      .scrollbar::after {
        content: "";
        position: absolute;
        left: 17px;
        top: 3px;
        width: 57%;
        height: 6px;
        border-radius: 999px;
        background: #a8a8a8;
      }

      .playground h1 {
        margin: 0 0 16px;
        font-size: 2rem;
        font-weight: 600;
      }

      .playground-copy {
        margin: 0 0 17px;
        font-size: 1rem;
        color: var(--text);
      }

      .response-box,
      .status-box,
      .json-box {
        border: 1px solid var(--border);
        background: transparent;
      }

      .response-box {
        min-height: 90px;
        padding: 11px 12px;
      }

      .response-box label {
        display: block;
        margin-bottom: 12px;
        font-size: 1rem;
        color: var(--text);
      }

      textarea {
        width: 100%;
        min-height: 34px;
        padding: 0;
        border: 0;
        outline: 0;
        resize: vertical;
        background: transparent;
        color: var(--muted);
        font: inherit;
        font-size: 0.95rem;
        font-family: "Segoe UI", sans-serif;
      }

      .button-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
      }

      button {
        padding: 11px 12px;
        border: 1px solid var(--border);
        border-top: 0;
        background: var(--surface-2);
        color: var(--text);
        font: inherit;
        font-size: 0.95rem;
        cursor: pointer;
      }

      button + button {
        border-left: 0;
      }

      button:hover {
        background: #343a45;
      }

      .status-box {
        min-height: 78px;
        padding: 12px;
        border-top: 0;
      }

      .status-title {
        margin: 0 0 12px;
        font-size: 1rem;
        color: var(--text);
      }

      .status-text {
        margin: 0;
        font-size: 0.95rem;
        color: var(--muted);
        line-height: 1.45;
      }

      .json-box {
        margin-top: 17px;
        border: 2px solid var(--border-strong);
        min-height: 268px;
        position: relative;
      }

      .json-tag {
        position: absolute;
        top: -1px;
        left: -1px;
        padding: 5px 10px;
        background: #1a1f29;
        border-right: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        color: var(--muted);
        font-size: 0.88rem;
      }

      .json-box pre {
        margin: 0;
        min-height: 264px;
        padding: 36px 14px 14px;
        overflow: auto;
        color: #dfe3ea;
        font-family: Consolas, monospace;
        font-size: 0.9rem;
        line-height: 1.45;
      }

      @media (max-width: 980px) {
        .layout {
          grid-template-columns: 1fr;
        }
=======
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
>>>>>>> cstech
      }
    </style>
  </head>
  <body>
    <main>
<<<<<<< HEAD
      <div class="layout">
        <aside class="sidebar">
          <div class="sidebar-header">
            <h2>Quick Start</h2>
            <div class="caret">▼</div>
          </div>

          <section class="sidebar-section">
            <p class="sidebar-copy">Connect to this environment</p>
            <p class="sidebar-subtitle">
              Connect from Python using <span class="inline-code">CyberVulnerabilityTriageEnv</span>:
            </p>
            <div class="code-card">
              <div class="copy-icon">⧉</div>
              <pre><span class="py-keyword">from</span> <span class="py-name">cyber_vulnerability_triage</span> <span class="py-keyword">import</span> <span class="py-class">CyberVulnerabilityTriageEnv</span>

<span class="py-keyword">async with</span> <span class="py-class">CyberVulnerabilityTriageEnv</span>.<span class="py-func">from_env</span>(<span class="py-string">"__SPACE_ID__"</span>) <span class="py-keyword">as</span> <span class="py-name">env</span>:
    <span class="py-name">result</span> <span class="py-op">=</span> <span class="py-keyword">await</span> <span class="py-name">env</span>.<span class="py-func">reset</span>(<span class="py-name">task</span><span class="py-op">=</span><span class="py-string">"medium"</span>)
    <span class="py-name">result</span> <span class="py-op">=</span> <span class="py-keyword">await</span> <span class="py-name">env</span>.<span class="py-func">step</span>({
        <span class="py-string">"action_type"</span>: <span class="py-string">"inspect_payload"</span>
    })</pre>
              <div class="scrollbar"></div>
            </div>
          </section>

          <section class="sidebar-section">
            <p class="sidebar-subtitle">Or connect directly to a running server:</p>
            <div class="code-card">
              <div class="copy-icon">⧉</div>
              <pre><span class="py-name">env</span> <span class="py-op">=</span> <span class="py-class">CyberVulnerabilityTriageEnv</span>(
    <span class="py-name">base_url</span><span class="py-op">=</span><span class="py-string">"__BASE_URL__"</span>
)</pre>
              <div class="scrollbar"></div>
            </div>
          </section>

          <section class="sidebar-section">
            <p class="sidebar-copy">Contribute to this environment</p>
            <p class="sidebar-subtitle">Submit improvements via pull request on the Hugging Face Hub.</p>
            <div class="code-card">
              <div class="copy-icon">⧉</div>
              <pre>openenv fork tejas49167-ui/OpenEnv-cyber-vulnerability-triage</pre>
              <div class="scrollbar"></div>
            </div>
            <p class="sidebar-subtitle" style="margin-top:12px;">Then make your changes and submit a pull request:</p>
            <div class="code-card">
              <div class="copy-icon">⧉</div>
              <pre>cd &lt;forked-repo&gt;
openenv push tejas49167-ui/OpenEnv-cyber-vulnerability-triage --create-pr</pre>
              <div class="scrollbar"></div>
            </div>
            <div class="meta-links">
              <a href="__DOCS_HREF__">Docs</a>
              <a href="__HEALTH_HREF__">Health</a>
              <a href="__BENCHMARK_HREF__">Benchmark</a>
            </div>
          </section>
        </aside>

        <section class="playground">
          <h1>Playground</h1>
          <p class="playground-copy">Click <strong>Reset</strong> to start a new cyber triage episode.</p>

          <div class="response-box">
            <label for="responseInput">Response</label>
            <textarea id="responseInput" placeholder="Enter action JSON..."></textarea>
          </div>

          <div class="button-row">
            <button id="stepBtn" type="button">Step</button>
            <button id="resetBtn" type="button">Reset</button>
            <button id="stateBtn" type="button">Get state</button>
          </div>

          <div class="status-box">
            <p class="status-title">Status</p>
            <p class="status-text" id="statusText">Ready.</p>
          </div>

          <div class="json-box">
            <div class="json-tag">&lt;/&gt; Raw JSON response</div>
            <pre id="jsonOutput">{
  "status": "ready"
}</pre>
          </div>
        </section>
      </div>
    </main>

    <script>
      const basePath = __BASE_PATH_JSON__;
      const baseUrl = basePath || "";
      const responseInput = document.getElementById("responseInput");
      const jsonOutput = document.getElementById("jsonOutput");
      const statusText = document.getElementById("statusText");
      const buttons = Array.from(document.querySelectorAll("button"));

      function setBusy(isBusy) {
        for (const button of buttons) {
          button.disabled = isBusy;
        }
      }

      function setStatus(text) {
        statusText.textContent = text;
      }

      function renderJson(payload) {
        jsonOutput.textContent = JSON.stringify(payload, null, 2);
      }

      function parseActionInput() {
        const raw = responseInput.value.trim();
        if (!raw) {
          return { action_type: "inspect_payload" };
        }
        return JSON.parse(raw);
      }

      async function callApi(path, options, label) {
        setBusy(true);
        try {
          const response = await fetch(`${baseUrl}${path}`, options);
          const rawText = await response.text();
          let payload;
          try {
            payload = rawText ? JSON.parse(rawText) : {};
          } catch {
            payload = { error: rawText || `HTTP ${response.status}` };
          }
          renderJson(payload);
          if (!response.ok) {
            setStatus(payload.detail || payload.error || `${label} failed.`);
            return null;
          }
          return payload;
        } catch (error) {
          const payload = { error: String(error) };
          renderJson(payload);
          setStatus(`${label} failed.`);
          return null;
        } finally {
          setBusy(false);
        }
      }

      async function resetEpisode() {
        const payload = await callApi(
          "/reset",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task: "medium" }),
          },
          "Reset"
        );
        if (payload?.observation) {
          setStatus(`Started ${payload.observation.request_id}`);
          responseInput.value = JSON.stringify({ action_type: "inspect_payload" }, null, 2);
        }
      }

      async function getState() {
        const payload = await callApi("/state", { method: "GET" }, "Get state");
        if (payload) {
          setStatus(`Task ${payload.current_task || "unknown"}, steps ${payload.steps_taken ?? 0}`);
        }
      }

      async function stepEpisode() {
        let action;
        try {
          action = parseActionInput();
        } catch (error) {
          setStatus("Invalid JSON in Response box.");
          renderJson({ error: String(error) });
          return;
        }
        const payload = await callApi(
          "/step",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(action),
          },
          "Step"
        );
        if (payload?.observation) {
          setStatus(payload.observation.metadata?.reward?.feedback || "Step complete.");
        }
      }

      document.getElementById("resetBtn").addEventListener("click", resetEpisode);
      document.getElementById("stateBtn").addEventListener("click", getState);
      document.getElementById("stepBtn").addEventListener("click", stepEpisode);
    </script>
  </body>
</html>
"""
        .replace("__BASE_PATH_JSON__", json.dumps(base_path))
        .replace("__BASE_URL__", f"{base_path or ''}")
        .replace("__SPACE_ID__", "tejas49167-ui/OpenEnv-cyber-vulnerability-triage")
        .replace("__DOCS_HREF__", f"{base_path}/docs")
        .replace("__HEALTH_HREF__", f"{base_path}/health")
        .replace("__BENCHMARK_HREF__", f"{base_path}/benchmark")
    )
=======
      <section class="hero">
        <span class="eyebrow">Sec-OpenEnv</span>
        <h1>Cyber Vulnerability Triage</h1>
        <p>
          This deployment exposes the flagship Sec-OpenEnv security environment:
          realistic alert triage with structured analyst actions, deterministic
          grading, and a deployment-ready OpenEnv-compatible API.
        </p>
        <div class="actions">
          <a class="button primary" href="/docs">Open API Docs</a>
          <a class="button secondary" href="/health">Health Check</a>
          <a class="button secondary" href="/benchmark">Benchmark Info</a>
        </div>
      </section>

      <section class="grid">
        <article class="card">
          <h2>Why It’s Useful</h2>
          <ul>
            <li>Models a realistic analyst workflow, not a one-shot classifier.</li>
            <li>Uses deterministic cases for reproducible evaluation.</li>
            <li>Works as both a browser-friendly demo and a framework-ready API service.</li>
          </ul>
        </article>

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
>>>>>>> cstech
