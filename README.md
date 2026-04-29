# Scibudy

[![CI](https://github.com/ONEMULE/scibudy/actions/workflows/ci.yml/badge.svg)](https://github.com/ONEMULE/scibudy/actions/workflows/ci.yml)
[![Docs](https://github.com/ONEMULE/scibudy/actions/workflows/docs.yml/badge.svg)](https://github.com/ONEMULE/scibudy/actions/workflows/docs.yml)
[![Release Check](https://github.com/ONEMULE/scibudy/actions/workflows/release-check.yml/badge.svg)](https://github.com/ONEMULE/scibudy/actions/workflows/release-check.yml)

Scibudy is a Codex-native scientific research assistant for scholarly search, reusable paper libraries, full-text analysis, and local semantic evidence retrieval.

It is useful when you want Codex or a shell workflow to collect papers, organize a local corpus, ingest PDFs and article pages, search evidence inside that corpus, and generate structured research notes without scattering state across the source checkout.

Scibudy is not a reference manager replacement, a guaranteed full-text downloader for paywalled articles, or a substitute for reading and verifying cited papers yourself.

中文简介：

Scibudy 是一个面向 Codex 的科研增强助手，提供学术检索、文献库管理、全文分析、本地证据检索和期刊文风分析能力。它既可以作为 MCP 工具，也可以作为独立 CLI 和本地管理界面使用。

## Status

- License: Apache-2.0
- Current release: `v0.3.0`
- Release posture: stable `v0.x` user workflows with explicitly documented limits
- Primary platforms: Linux and macOS
- Full local GPU path: Linux + NVIDIA + conda first

## Quick links

- Docs Pages: <https://onemule.github.io/SciBudy/>
- GitHub Releases: <https://github.com/ONEMULE/scibudy/releases>
- npm installer: <https://www.npmjs.com/package/scibudy-installer>
- PyPI package: <https://pypi.org/project/scibudy/>
- English docs: [docs/en/index.md](docs/en/index.md)
- 中文文档: [docs/zh/index.md](docs/zh/index.md)
- Prerequisites: [docs/en/prerequisites.md](docs/en/prerequisites.md) / [docs/zh/prerequisites.md](docs/zh/prerequisites.md)
- Codex MCP setup: [docs/en/codex-setup.md](docs/en/codex-setup.md) / [docs/zh/codex-setup.md](docs/zh/codex-setup.md)
- Usage examples: [docs/en/examples.md](docs/en/examples.md) / [docs/zh/examples.md](docs/zh/examples.md)
- Journal style analysis: [docs/en/journal-style-analysis.md](docs/en/journal-style-analysis.md) / [docs/zh/journal-style-analysis.md](docs/zh/journal-style-analysis.md)
- Architecture: [docs/en/architecture.md](docs/en/architecture.md) / [docs/zh/architecture.md](docs/zh/architecture.md)
- Support matrix: [docs/en/support-matrix.md](docs/en/support-matrix.md) / [docs/zh/support-matrix.md](docs/zh/support-matrix.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security: [SECURITY.md](SECURITY.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Roadmap: [ROADMAP.md](ROADMAP.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## Five-minute start

Requirements for the base path are Node.js 18+ and Python 3.10+.

```bash
npx scibudy-install --profile base
scibudy doctor --json
scibudy install-codex
codex mcp get research
scibudy search "simulation-based calibration"
scibudy ui --open
```

Use `scibudy doctor --json` to confirm provider readiness, app-home paths, Codex config state, and missing optional credentials.

## Install choices

| Path | Best for | Command |
| --- | --- | --- |
| npm installer | New users and Codex users who want the managed runtime | `npx scibudy-install --profile base` |
| Source install | Contributors or users testing unreleased changes | `python -m pip install -e .[dev]` then `scibudy bootstrap --profile base --install-codex` |
| GPU local | Linux NVIDIA users who want local embedding and reranking models | `npx scibudy-install --profile gpu-local` |
| Developer install | Repo development, tests, docs, and package checks | `python -m pip install -e .[dev,docs,release]` |

Profiles:

- `base`: search, library management, UI, and Codex MCP config
- `analysis`: base plus analysis-oriented runtime conventions
- `gpu-local`: local GPU model environment and cache warm flow
- `full`: base, analysis, and GPU-local setup together

Detailed setup:

- English: [docs/en/installation.md](docs/en/installation.md)
- 中文: [docs/zh/installation.md](docs/zh/installation.md)

## Common workflows

### Search literature

```bash
scibudy search "posterior calibration in simulation-based inference" --mode general --limit 20
```

### Build a reusable paper library

```bash
scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library --limit 50
scibudy libraries
```

### Ingest and analyze full text

```bash
scibudy ingest-library <library_id>
scibudy analyze-topic <library_id> calibration
scibudy search-evidence <library_id> "posterior coverage"
scibudy synthesize-library <library_id> "calibration in simulation-based inference" --profile auto
```

### Analyze journal writing style

```bash
scibudy journal-analyze \
  --journal nature-communications \
  --query "atmospheric chemistry Bayesian inference" \
  --target-dir ./nc-style \
  --target-size 100
```

### Use from Codex

After `scibudy install-codex`, verify the managed MCP block:

```bash
codex mcp get research
```

Then ask Codex to call the high-level workflow:

```text
Use research_workflow with query="calibration methods in simulation-based inference", mode="general", limit=50, synthesize=true.
```

Use lower-level MCP tools such as `search_literature`, `collect_library`, `ingest_library`, `search_library_evidence`, and `build_research_synthesis` when you need manual control.

## CLI surfaces

- `scibudy`
- `scibudy-mcp`
- Compatibility aliases: `research-cli`, `research-mcp`

Examples:

```bash
scibudy search "simulation-based calibration" --mode general
scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library
scibudy journal-analyze --journal nature-communications --query "atmospheric chemistry Bayesian inference" --target-dir ~/Desktop/nc-style
scibudy analysis-settings
scibudy ingest-library <library_id>
scibudy search-evidence <library_id> calibration
scibudy profiles
scibudy workflow "calibration methods in simulation-based inference" --limit 50 --topic "calibration in simulation-based inference"
scibudy workflow "calibration methods in simulation-based inference" --dry-run
scibudy workflow "calibration methods in simulation-based inference" --quality-mode fast
scibudy security-audit
scibudy doctor --install-readiness
scibudy synthesize-library <library_id> "causal inference robustness" --profile general
scibudy synthesize-library <library_id> "calibration in simulation-based inference" --profile sbi_calibration
scibudy ui --open
```

Use `dry_run=true` when an agent should preview writes and planned steps before executing. Use `quality_mode=fast` for low-cost exploration, `standard` for the normal workflow, and `deep` when missing full text or unsupported claims require stricter follow-up.

For safer agent automation, run `scibudy security-audit` and `scibudy doctor --install-readiness` before delegating long-running research workflows.

## Domain profiles

Domain profiles do **not** limit Scibudy's search scope or providers. Search remains general and multi-source by default.

Profiles only tune full-text synthesis: section weighting, evidence markers, unsupported-claim detection, and risk flags.

- `general`: default all-domain synthesis profile.
- `auto`: chooses a synthesis profile from the topic while preserving general search.
- `sbi_calibration`: an example preset for simulation-based inference calibration workflows.

For more examples and Codex prompt patterns:

- English: [docs/en/examples.md](docs/en/examples.md)
- 中文: [docs/zh/examples.md](docs/zh/examples.md)

## Local model stack

The highest-quality local retrieval path currently uses:

- `Qwen/Qwen3-Embedding-4B`
- `Qwen/Qwen3-Reranker-4B`

Recommended workflow:

```bash
scibudy install-local-models
scibudy warm-local-models --background
```

See:

- English: [docs/en/gpu-local.md](docs/en/gpu-local.md)
- 中文: [docs/zh/gpu-local.md](docs/zh/gpu-local.md)

## Safety and data model

- Runtime state lives in the app home, not in the source directory. The default app home is `~/.research-mcp`; override it with `RESEARCH_MCP_HOME=/custom/path`.
- API keys and provider credentials are written to the app-home `.env` file. Do not commit that file.
- Source installs and npm installs share the same runtime commands, but generated libraries, caches, reports, and UI state stay outside the repo unless you explicitly choose a repo path.
- GPU-local mode expects a Linux NVIDIA machine with conda. Base and analysis workflows do not require GPU models.
- Scibudy records missing provider credentials and degraded search providers in `scibudy doctor --json` instead of failing silently.

## Repository layout

```text
research_mcp/   Python runtime, MCP server, CLI, analysis engine
web/            UI source and built assets
bin/            npm/bootstrap entrypoints
docs/           Bilingual project documentation
examples/       Copyable usage examples
scripts/        Release and smoke-check helpers
.github/        CI, templates, automation
```

## Open-source project standards

This repository is intentionally organized like a professional open-source library:

- documented install profiles
- release manifest and bootstrap state
- contributor and support policies
- issue/PR templates
- CI and packaging checks
- bilingual documentation for core user workflows

## Development

Core local checks:

```bash
make test
make build-ui
make package-check
make release-check
```

For deeper guidance:

- English: [docs/en/development.md](docs/en/development.md)
- 中文: [docs/zh/development.md](docs/zh/development.md)
