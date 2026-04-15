# Development

## Tooling

- Python runtime in `.venv`
- frontend in `web/`
- npm bootstrap wrapper in `bin/`

## Common commands

```bash
make test
make build-ui
make package-check
make release-check
```

## Development principles

- keep CLI/MCP behavior explicit
- keep install/runtime separation intact
- do not commit user state or secrets
- update docs with public behavior changes

## Important subsystems

- search providers
- catalog/library management
- analysis engine
- local model workers
- installer/bootstrap layer
