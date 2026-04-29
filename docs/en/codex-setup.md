# Codex MCP Setup

Scibudy exposes a local `stdio` MCP server named `research`. Once configured, Codex can call Scibudy tools for search, library creation, ingestion, evidence retrieval, synthesis, and journal-style analysis.

## Automatic setup

Use the installer or bootstrap flow:

```bash
npx scibudy-install --profile base
scibudy install-codex
codex mcp get research
```

Or from a source checkout:

```bash
scibudy bootstrap --profile base --install-codex
codex mcp get research
```

`scibudy install-codex` updates the managed `research` MCP block in:

```text
~/.codex/config.toml
```

It points Codex at `research-mcp` or `scibudy-mcp`, depending on the installed runtime.

## Manual setup

If you do not want Scibudy to edit Codex config automatically, bootstrap without Codex changes:

```bash
scibudy bootstrap --profile base --no-install-codex
```

Then add a `research` MCP server in Codex that uses:

```text
transport: stdio
command: research-mcp
```

Use the absolute command path when Codex cannot resolve the command from its login environment.

## Verify

```bash
codex mcp get research
```

Expected signals:

- server name is `research`
- transport is `stdio`
- command points to `research-mcp` or `scibudy-mcp`
- the server exposes search, open-access, library, analysis, synthesis, and UI tools

For runtime readiness:

```bash
scibudy doctor --json
scibudy security-audit
```

## Typical Codex prompts

```text
Search recent literature on posterior calibration in simulation-based inference using research_workflow. Use dry_run=true first.
```

```text
Use collect_library to build a local library for "Bayesian atmospheric chemistry inverse modeling", then ingest_library and search_library_evidence for "uncertainty calibration".
```

```text
Run analyze_journal_style for nature-communications with query "atmospheric chemistry Bayesian inference" and summarize the output files.
```

## Troubleshooting

If Codex cannot see the MCP server:

```bash
scibudy install-codex
codex mcp get research
scibudy doctor --json
```

If the command path is missing in an SSH or GUI-launched Codex session, reinstall with Scibudy or edit the MCP block to use an absolute path to `research-mcp`.
