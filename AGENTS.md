# Repository Guidelines

## Project Structure & Module Organization

Scibudy is a Python-first research assistant with a small web UI and npm bootstrap wrapper. Core runtime code lives in `research_mcp/`, including the CLI, MCP server, providers, library management, ranking, and analysis engine. Tests live in `tests/` and mirror runtime modules with `test_*.py` files. The React/Vite UI is under `web/`, with source in `web/src/` and package metadata in `web/package.json`. Documentation is bilingual under `docs/en/` and `docs/zh/`; release, smoke, and site checks live in `scripts/`. Installer entrypoints are in `bin/`, and public examples are in `examples/`.

## Build, Test, and Development Commands

Create a local environment with:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
```

Run `make verify-local` for ordinary changes; it covers tests, the Vite UI build, strict docs build, npm package validation, and release/config consistency checks. For Pages, installer, or release metadata changes, run `make verify-full` so the live Pages health check also runs against `https://onemule.github.io/SciBudy/`. Use individual targets such as `make test`, `make build-ui`, `make build-docs`, `make package-check`, and `make release-check` when narrowing a failure.

## Coding Style & Naming Conventions

Follow `.editorconfig`: UTF-8, LF line endings, final newline, no trailing whitespace, spaces by default, 4-space Python indentation, and tabs only in `Makefile`. Python modules and functions use `snake_case`; classes use `PascalCase`. Keep public CLI and MCP behavior backward compatible, and update docs when user-facing behavior changes. JavaScript files are ESM; keep the installer syntax valid with `node --check bin/scibudy-install.mjs`.

## Testing Guidelines

Pytest is the primary test framework. Add or update tests in `tests/` for behavior changes, especially provider logic, ranking, config handling, library state, and service behavior. Prefer deterministic tests that do not require live credentials or network access. Run `pytest -q` directly or `make test`; CI also compiles `research_mcp` and builds the UI.

## Commit & Pull Request Guidelines

Recent history uses concise imperative summaries, often squash-merged with PR numbers, such as `Fix Site Health Pages URL casing (#27)`. Keep commits focused. A pull request should include a short change summary, tests run, documentation updates for public changes, linked issues when applicable, and screenshots for UI changes. Call out release-sensitive changes to install logic, Codex config management, package metadata, or public CLI/MCP interfaces.

## Security & Configuration Tips

Do not commit secrets, runtime logs, local state, cached analysis outputs, or user libraries. Use `.env.example` for documented configuration shape only. Before long automation or release work, run `scibudy security-audit` and `scibudy doctor --install-readiness` when available.
