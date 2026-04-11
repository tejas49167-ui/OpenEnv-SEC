# Sec-OpenEnv

Sec-OpenEnv is a framework-oriented repository for security environments that can be benchmarked, served, and extended using a shared OpenEnv-style contract.

The current flagship environment, **Cyber Vulnerability Triage**, preserves the original benchmark semantics:

- suspicious HTTP requests are presented as analyst queue items
- agents investigate using structured actions
- final triage decisions are graded deterministically

```{toctree}
:maxdepth: 1

quickstart
architecture
environments
extensibility
security-model
roadmap
```
