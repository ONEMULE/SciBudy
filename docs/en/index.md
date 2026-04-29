# Scibudy Documentation

Scibudy is a Codex-native research assistant for scholarly search, reusable paper libraries, full-text analysis, local evidence retrieval, and journal-style diagnostics.

## Core surfaces

- CLI: `scibudy`
- MCP server: `scibudy-mcp`
- Installer: `scibudy-install`
- UI: `scibudy ui --open`

## Five-minute path

```bash
npx scibudy-install --profile base
scibudy doctor --json
scibudy install-codex
codex mcp get research
scibudy search "simulation-based calibration"
scibudy ui --open
```

## Documentation map

- [Prerequisites](prerequisites.md)
- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Codex MCP setup](codex-setup.md)
- [CLI and MCP](cli-and-mcp.md)
- [Examples](examples.md)
- [Configuration](configuration.md)
- [GPU local models](gpu-local.md)
- [Library workflow](library-workflow.md)
- [Journal style analysis](journal-style-analysis.md)
- [Troubleshooting](troubleshooting.md)
- [Development](development.md)
- [Releasing](releasing.md)

## Release links

- GitHub Releases: <https://github.com/ONEMULE/scibudy/releases>
- npm installer: <https://www.npmjs.com/package/scibudy-installer>
- PyPI package: <https://pypi.org/project/scibudy/>

## Architecture summary

Scibudy is Python-first:

- `research_mcp/` contains the runtime, MCP server, CLI, and analysis stack
- `web/` contains the UI source and distributable build artifacts
- `bin/scibudy-install.mjs` is the npm/bootstrap wrapper
- user runtime state is stored under the app home, not in the source tree

## Product model

- `base` profile: CPU-safe runtime and Codex integration
- `analysis` profile: full-text analysis workflow
- `gpu-local` profile: local model environment
- `full` profile: all layers together
