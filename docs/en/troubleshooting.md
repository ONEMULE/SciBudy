# Troubleshooting

Start with:

```bash
scibudy doctor --json
```

The JSON output reports app-home paths, provider readiness, missing credentials, Codex config state, local model status, and suggested next steps.

## npm says you are not logged in

Normal users do not need npm login to install:

```bash
npx scibudy-install --profile base
```

`npm whoami` only matters when publishing the installer package. If you are releasing from a local machine, run `npm login`; otherwise let GitHub Actions publish with repository secrets.

## Python version is too old

Scibudy requires Python 3.10+:

```bash
python3 --version
```

Install a newer Python or create a virtual environment with a supported interpreter, then reinstall:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
```

## Codex cannot find the MCP server

Run:

```bash
scibudy install-codex
codex mcp get research
scibudy doctor --json
```

If the MCP block exists but Codex still fails, use an absolute path to `research-mcp` or `scibudy-mcp` in `~/.codex/config.toml`. This is common when Codex starts from a GUI or SSH login shell with a different `PATH`.

## Docs Pages URL does not load

Use the exact Pages URL:

```text
https://onemule.github.io/SciBudy/
```

The `SciBudy` path casing matters.

## GPU local setup is not supported

The full local model stack assumes:

- Linux
- NVIDIA GPU and working drivers
- conda
- enough disk and VRAM for `Qwen/Qwen3-Embedding-4B` and `Qwen/Qwen3-Reranker-4B`

If this is not your machine, use `base` or `analysis` instead:

```bash
npx scibudy-install --profile base
```

## Local model environment not found

Run:

```bash
scibudy install-local-models
scibudy warm-local-models --background
scibudy analysis-settings
```

If conda is missing or the GPU path is unsupported, Scibudy can still use CPU-safe search and provider-backed analysis paths.

## Missing API key or provider degraded

Run:

```bash
scibudy setup
scibudy doctor --json
```

Strongly recommended keys include `CROSSREF_MAILTO`, `UNPAYWALL_EMAIL`, and `OPENALEX_API_KEY`. Optional keys such as `SEMANTIC_SCHOLAR_API_KEY`, `NCBI_API_KEY`, `CORE_API_KEY`, and `OPENAI_API_KEY` improve coverage, rate limits, or analysis quality.

## OpenAI key is configured but not used

Check analysis settings:

```bash
scibudy analysis-settings
```

If quota, model access, or network access fails, Scibudy falls back where possible and reports the degraded provider state in `doctor`.

## UI does not open

Run:

```bash
scibudy doctor --json
scibudy ui --open
```

If the UI asset check fails, rerun the installer or bootstrap so the app-home copy of `ui/dist/index.html` is refreshed.

## Journal-style PDF report is missing

Markdown and CSV outputs do not require a PDF toolchain. The optional PDF report requires:

- `pandoc`
- `xelatex`

Run without `--pdf-report` or install those tools locally.
