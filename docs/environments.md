# Environments

Sec-OpenEnv treats environments as first-class modules inside a shared framework, not as one-off scripts.

## Bundled Environment

### Cyber Vulnerability Triage

Purpose:

- simulate a realistic web security alert triage workflow
- preserve deterministic grading and case selection
- expose a standard environment API for local and remote execution

Tasks:

- `easy`: classify the vulnerability family
- `medium`: classify the vulnerability family and severity
- `hard`: perform a full triage decision including response action and explanation

## Environment Contract

Each environment in Sec-OpenEnv should expose:

- clear task definitions
- typed action and observation models
- deterministic or explicitly documented state transitions
- a server surface for `reset`, `step`, `state`, `metadata`, and `health`
- examples and tests

## Current Layout

- `src/sec_openenv/environments/cyber_vulnerability_triage/`: framework-facing package
- `src/cyber_vulnerability_triage/`: backward-compatible imports
- `env/`: benchmark internals and task logic
