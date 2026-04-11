# Project Layout

This repository mixes two needs:

1. a clean framework-style `src/` layout for growth
2. a small set of compatibility modules for older entrypoints

For hackathon work, use the structure below as the default map.

## Canonical Layout

```text
.
├── src/
│   ├── sec_openenv/                 # framework package, CLI, registry
│   └── cyber_vulnerability_triage/  # public environment package exports
├── env/                             # benchmark mechanics and deterministic task logic
├── server/                          # FastAPI app for the demoable API surface
├── examples/                        # runnable demos and benchmark walkthroughs
├── tests/                           # regression coverage
├── configs/                         # environment descriptors/config files
├── docs/                            # architecture and contributor documentation
├── outputs/                         # local artifacts from evals and logs
└── assets/                          # static branding and doc assets
```

## Practical Rules

- Add framework code under `src/sec_openenv/`.
- Add environment-specific modules under `src/sec_openenv/environments/<slug>/`.
- Add public demos and scripts under `examples/`.
- Keep one-off outputs in `outputs/`.
- Avoid adding new top-level Python packages unless there is a compatibility reason.

## Compatibility Notes

- Root `app.py` is a lightweight wrapper around `server.app`.
- Root `client.py` and `inference.py` remain useful shortcuts, but new reusable code should live under `src/`.
- `env/`, `server/`, `agent/`, and `graders/` are still active for the cyber triage benchmark and should be treated as part of the current product, not dead code.
