# Quickstart

This path starts from a clean machine with Node.js 18+ and Python 3.10+. It installs the base runtime, verifies it, connects Codex, runs a search, creates a library, and opens the browser UI.

## 1. Install the base runtime

```bash
npx scibudy-install --profile base
```

The installer creates or updates the Scibudy runtime and keeps local state in the app home, normally `~/.research-mcp`.

## 2. Verify the install

```bash
scibudy doctor --json
```

Check these fields first:

- `status`: overall readiness.
- `app_home`: where Scibudy keeps runtime state.
- `provider_statuses`: which search providers are ready.
- `missing_credentials`: optional keys that would improve coverage.
- `codex_configured`: whether Codex already has the managed MCP block.

## 3. Connect Codex

```bash
scibudy install-codex
codex mcp get research
```

You should see a `stdio` MCP server named `research`. If Codex is not installed on this machine, skip this step and use the CLI directly.

## 4. Run your first search

```bash
scibudy search "simulation-based calibration" --limit 10
```

Use `--mode biomed` for biomedical searches and `--sort recent` when recency matters more than relevance.

## 5. Build a local library

```bash
scibudy collect "simulation-based calibration" \
  --target-dir ~/Desktop/sbc-library \
  --limit 30
```

This writes organized metadata, Markdown, BibTeX, and PDF download results when open-access PDFs are available. Paywalled or unavailable PDFs are listed for manual follow-up instead of being fabricated.

## 6. Ingest and analyze the library

```bash
scibudy libraries
scibudy ingest-library <library_id>
scibudy analyze-topic <library_id> calibration
scibudy search-evidence <library_id> "posterior coverage"
```

Use the `library_id` returned by `scibudy libraries` or the collect command.

## 7. Open the UI

```bash
scibudy ui --open
```

The UI is a local browser manager for libraries, items, analysis settings, context bundles, and generated reports.

## 8. Ask Codex to run the workflow

After MCP setup, use a prompt like:

```text
Use research_workflow with query="calibration methods in simulation-based inference", mode="general", limit=50, synthesize=true.
```

For safer automation, ask for `dry_run=true` first or use `quality_mode=fast` for a low-cost search and library setup pass.
