# Contributing to Scibudy

Thank you for contributing.

## Project expectations

Scibudy is organized as a professional open-source toolchain:

- Python is the canonical runtime
- npm is the bootstrap/distribution wrapper
- Linux is the reference platform for full local GPU support
- documentation and examples are treated as product surface, not optional extras

## Local development

### 1. Clone and install

```bash
git clone git@github.com:ONEMULE/scibudy.git
cd scibudy
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
```

### 2. Frontend build

```bash
cd web
npm install
npm run build
cd ..
```

### 3. Core checks

```bash
make test
make build-ui
make package-check
```

## Contribution guidelines

- Keep runtime behavior deterministic where possible.
- Prefer backward-compatible CLI and MCP changes.
- Treat install/upgrade paths as first-class product behavior.
- Update docs when adding or changing public behavior.
- Do not commit secrets, runtime logs, user state, or local analysis outputs.

## Pull requests

A good pull request includes:

- a concise change summary
- tests for behavior changes
- updated documentation for public changes
- release-note worthy changes called out explicitly

## Release-sensitive areas

Extra care is required when changing:

- bootstrap/install logic
- Codex config management
- local model environment management
- public CLI/MCP interfaces
- package metadata and release manifest behavior
