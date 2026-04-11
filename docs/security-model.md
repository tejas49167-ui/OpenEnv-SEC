# Security Model

Sec-OpenEnv is a simulation and benchmarking framework, not a live detection or response system.

## Security Posture

- environment cases are deterministic and repository-contained
- no live customer traffic is required
- the server exposes a small, explicit API surface
- model-provider access is optional and environment-variable driven

## Trust Boundaries

- repository code
- local runtime
- external model providers
- HTTP clients

## Relevant Risks

- accidental secret exposure through `.env` usage
- unsafe public deployment of the demo server
- benchmark drift without documentation
- unreviewed grading changes that affect determinism
