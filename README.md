# Cybersecurity Web Vulnerability Triage Environment

## Environment Description

This project implements a production-quality OpenEnv-style environment for web vulnerability triage. An agent receives realistic HTTP requests and must determine whether they are benign or malicious, classify severity, and choose the safest operational response.

## Real-World Motivation

Security teams routinely inspect application traffic for attacks such as reflected XSS, SQL injection, command injection, and directory traversal. This environment mirrors that workflow in a deterministic offline setting so models can be benchmarked on practical detection and triage behavior.

## Observation Space

The environment returns a Pydantic `Observation` model with:

- `task`
- `request_id`
- `method`
- `path`
- `headers`
- `query_params`
- `body`
- `source_ip`
- `user_agent`
- `instructions`

## Action Space

The agent must return a Pydantic `Action` model with:

- `vulnerability_type`: `safe`, `xss`, `sql_injection`, `command_injection`, `path_traversal`
- `severity`: `none`, `low`, `medium`, `high`, `critical`
- `response_action`: `allow`, `block`, `sanitize`
- `explanation`: short analyst-style reasoning

## Task Descriptions

- `easy`: detect the vulnerability type
- `medium`: detect the vulnerability type and severity
- `hard`: complete end-to-end triage with detection, severity, response action, and explanation

## Dataset

The built-in dataset contains 10 deterministic HTTP request examples covering:

- XSS
- SQL injection
- Command injection
- Path traversal
- Safe traffic

Each record includes ground-truth vulnerability type, severity, recommended action, and explanation keywords for deterministic grading.

## Grading And Rewards

Three deterministic graders are included:

- `easy`: 1.0 for correct vulnerability type, else 0.0
- `medium`: 0.5 for vulnerability match and 0.5 for severity match
- `hard`: partial scoring with:
  - `+0.4` vulnerability match
  - `+0.3` severity match
  - `+0.2` action correctness
  - `+0.1` explanation quality
  - harmful decisions penalized deterministically

All graders return scores in the `[0.0, 1.0]` range with no randomness.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How To Run Inference

Local deterministic fallback:

```bash
python inference.py
```

With an OpenAI-compatible endpoint:

```bash
export API_BASE_URL="https://your-openai-compatible-endpoint/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-token"
python inference.py
```

If the API request fails, the baseline agent automatically falls back to a deterministic heuristic action.

## Docker

```bash
docker build -t cyber-openenv .
docker run --rm cyber-openenv
```

## Baseline Scores

Using the built-in deterministic fallback heuristic, the expected scores are:

- `easy`: 1.000
- `medium`: 1.000
- `hard`: 1.000
- `overall`: 1.000

## Project Structure

```text
cyber-openenv/
├── agent/
├── env/
├── graders/
├── inference.py
├── openenv.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```
