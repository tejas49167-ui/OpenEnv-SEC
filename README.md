
# Cyber OpenEnv (web alert triage)

![Work hell](https://wallpaperaccess.com/full/5996656.jpg)

This project is like a practice lab for **web security alert triage**.

In real companies, security people get alerts like “this HTTP request looks suspicious”.
They don’t just say “attack / not attack” in one second.
They look at the request, gather some clues, and then decide what to do (allow, block, sanitize, monitor).

This repo makes that whole workflow into an OpenEnv environment so an AI agent can learn it with the normal:

- `reset()` → start a new case
- `step()` → do one investigation action, or submit final decision
- `state()` → see internal progress

## What problem this solves (simple)

You want a place where you can test an agent on a real-ish security workflow:

- agent gets an alert (HTTP request)
- agent investigates step by step
- agent submits: **what attack is it**, **how severe**, **what response action**
- environment gives a score from **0.0 to 1.0**

So you can compare agents/prompts/models and see which one is actually better.

## How a single episode feels

Think of 1 episode as 1 suspicious request.

At first you only see basic request info.
Then the agent can do actions like:

- inspect payload (what user sent)
- decode obfuscation (maybe it is encoded)
- review history (did same IP do this before)
- check IP reputation
- inspect asset context (what app is this, is it sensitive)
- consult playbook (internal guidance)

Finally the agent does:

- `submit_triage` (final answer)

## Tasks / difficulty

The environment has 3 tasks in `env/tasks.py`:

- **Easy (Quick classification)**: mostly “what kind of thing is this?” (safe / xss / sql_injection / command_injection / path_traversal)
- **Medium (Severity + evidence)**: also decide severity (low/medium/high/critical) and show you did some investigation
- **Hard (Full triage workflow)**: full analyst mode: investigate, decide vulnerability + severity + response action, and give a short explanation

You will see `task` (id) and `task_label` (human text) in observations.

## What the agent can output (Action)

Agent sends a Pydantic `Action` (`env/models.py`):

- `action_type`: one of
  - `inspect_payload`
  - `decode_obfuscation`
  - `review_history`
  - `check_source_reputation`
  - `inspect_asset_context`
  - `consult_playbook`
  - `submit_triage`
- if it is `submit_triage`, then also send:
  - `vulnerability_type`: `safe | xss | sql_injection | command_injection | path_traversal`
  - `severity`: `none | low | medium | high | critical`
  - `response_action`: `allow | block | sanitize | monitor`
  - `explanation`: short text

## What the environment returns (Observation)

Observation is a typed Pydantic model (`env/models.py`).
It includes stuff like:

- request fields: `method`, `path`, `headers`, `query_params`, `body`, `source_ip`, `user_agent`
- instructions for the agent
- steps taken / remaining
- evidence log (what you already revealed)
- what actions are allowed next

## Dataset (the cases)

There are **12 cases** in `env/data.py`.
They cover:

- XSS
- SQL injection
- command injection
- path traversal
- also “benign but looks scary” traffic

Each case has ground truth labels + hidden artifacts that only show up if you investigate.

## Reward + grading (why it’s useful)

This is not only “final answer correct = 1 else 0”.

- When you investigate and reveal NEW evidence, you get some reward.
- If you keep repeating the same investigation, you get penalized.
- When you submit final triage, graders score it (0.0–1.0).
- Unsafe decisions can get extra penalty (example: allowing a clearly malicious request).

Graders are in `graders/` and are deterministic:

- `graders/easy_grader.py`
- `graders/medium_grader.py`
- `graders/hard_grader.py`

## Quick start (local)

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run baseline scoring:

```bash
python inference.py
```

## Run as an API (FastAPI)

The server is in `app.py`.

Run it:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 7860
```

Try it:

```bash
curl http://localhost:7860/health
curl -X POST http://localhost:7860/reset -H 'Content-Type: application/json' -d '{"task":"hard"}'
```

## Docker

Build:

```bash
docker build -t cyber-openenv .
```

Run API:

```bash
docker run --rm -p 7860:7860 cyber-openenv
```

Run baseline inside docker:

```bash
docker run --rm cyber-openenv python inference.py
```

## Repo map

```text
cyber-openenv/
├── agent/        # baseline agent
├── env/          # environment + models + tasks + reward
├── graders/      # scoring logic for easy/medium/hard
├── app.py        # FastAPI wrapper
├── inference.py  # runs baseline + prints scores
├── openenv.yaml  # OpenEnv metadata
├── Dockerfile
└── requirements.txt
```
