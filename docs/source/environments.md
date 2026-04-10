# Environment Layout

The canonical package is `cyber_vulnerability_triage/`, which mirrors the
structure used by OpenEnv example environments:

- `client.py` exposes the typed environment client
- `models.py` exposes public action and observation models
- `server/app.py` builds the FastAPI application
- `server/environment.py` aliases the actual environment implementation

The legacy root modules remain as compatibility shims so existing imports and
tests continue to work.

