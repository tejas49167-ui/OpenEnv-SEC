# Documentation

The `docs/` directory is the framework knowledge base for Sec-OpenEnv.

## Canonical Documents

- `architecture.md`
- `environments.md`
- `extensibility.md`
- `security-model.md`
- `roadmap.md`

## Supporting Docs

- `source/`: Sphinx entrypoints and lightweight wrappers
- `README.md`: this documentation index

## Build

```bash
make -C docs html
```

Generated HTML is written to `docs/build/html/`.
