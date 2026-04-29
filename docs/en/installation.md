# Installation

Choose the path that matches how you want to use Scibudy. The base path is the right default for most users: it installs the Python runtime, syncs the UI assets, and can add the managed Codex MCP block.

## Prerequisites

Required for the base profile:

- Node.js 18+
- Python 3.10+
- internet access for Python and npm package installation

Recommended:

- Codex installed when you want MCP integration
- Git when installing from source

Only the `gpu-local` and `full` profiles require Linux, NVIDIA GPU support, and conda.

## Install paths

| Path | Use when | Command |
| --- | --- | --- |
| npm installer | You want the normal user install | `npx scibudy-install --profile base` |
| source install | You are developing Scibudy or testing a checkout | `python -m pip install -e .[dev]` |
| GPU local | You want local Qwen embedding and reranking models | `npx scibudy-install --profile gpu-local` |
| developer install | You need tests, docs, build, and release tooling | `python -m pip install -e .[dev,docs,release]` |

## Recommended npm install

```bash
npx scibudy-install --profile base
scibudy doctor --json
```

The installer uses the release manifest to install `scibudy==0.3.0`, sync the browser UI, and set up runtime state under the app home. It does not write generated libraries or secrets into the source checkout.

Profiles:

- `base`: CLI, MCP server, UI assets, and Codex integration.
- `analysis`: base plus analysis-oriented runtime defaults.
- `gpu-local`: base plus a local GPU model environment and warm flow.
- `full`: all install layers together.

## Source install

```bash
git clone git@github.com:ONEMULE/scibudy.git
cd scibudy
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev,docs,release]
scibudy bootstrap --profile base --install-codex
scibudy doctor --json
```

Use a source install when you want to run tests, change code, or validate an unreleased branch.

## Codex MCP integration

Automatic setup:

```bash
scibudy install-codex
codex mcp get research
```

Or during bootstrap:

```bash
scibudy bootstrap --profile base --install-codex
codex mcp get research
```

The expected MCP block uses `stdio` and points to `research-mcp` or `scibudy-mcp`.

## Configure credentials

Scibudy can run without optional provider keys, but coverage and rate limits improve when you configure them:

```bash
scibudy setup
scibudy doctor --json
```

Credential values are stored in the app-home `.env` file. They are not written to the repository. Useful keys include `OPENALEX_API_KEY`, `CROSSREF_MAILTO`, `UNPAYWALL_EMAIL`, `SEMANTIC_SCHOLAR_API_KEY`, `NCBI_API_KEY`, `CORE_API_KEY`, and `OPENAI_API_KEY`.

## App home and data

Default app home:

```text
~/.research-mcp
```

Override it when you need a separate runtime:

```bash
export RESEARCH_MCP_HOME=/custom/path
```

Search runs, imported library metadata, generated reports, UI assets, local state, and `.env` live under the app home unless you explicitly pass another target directory.

## Upgrade

For npm-installed users:

```bash
npx scibudy-install --profile base
scibudy upgrade-runtime
scibudy doctor --json
```

For source installs:

```bash
git pull
python -m pip install -e .[dev,docs,release]
scibudy bootstrap --profile base --install-codex
```

## Uninstall or clean up

Remove the local GPU environment when you created one:

```bash
scibudy uninstall-local-models --yes
```

Then remove the app home only if you intentionally want to delete local Scibudy state:

```bash
rm -rf ~/.research-mcp
```

Also remove the managed `research` block from `~/.codex/config.toml` if you no longer want Codex to load Scibudy.
