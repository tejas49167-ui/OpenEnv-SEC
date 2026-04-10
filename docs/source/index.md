# Cyber Vulnerability Triage

An OpenEnv-compatible benchmark for multi-step cybersecurity alert triage.

This project keeps the original idea intact:

- analysts inspect suspicious HTTP requests
- the environment reveals evidence through structured actions
- agents submit a final triage decision with severity and response guidance

For the runtime API, use `server.app:app`. For the OpenEnv-style package API,
use `cyber_vulnerability_triage`.

See also:

- `quickstart.md` for local setup and example commands
- `architecture.md` for the package and benchmark layout
