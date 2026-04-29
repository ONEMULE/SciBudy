# Usage Examples

The examples below are copyable task templates. Replace topics, paths, and IDs with your own values.

## Ask Codex to collect literature

Use this after `scibudy install-codex` and `codex mcp get research` succeed:

```text
Use research_workflow with query="calibration methods in simulation-based inference", mode="general", limit=50, dry_run=true. Show me the planned writes before creating a library.
```

After reviewing the plan:

```text
Run the same research_workflow without dry_run. Use target_dir="~/Desktop/sbc-calibration-library", ingest=true, synthesize=true, topic="calibration in simulation-based inference", profile="auto".
```

## Build a library from the CLI

```bash
scibudy collect "calibration methods in simulation-based inference" \
  --mode general \
  --limit 50 \
  --target-dir ~/Desktop/sbc-calibration-library \
  --name "SBI calibration library"
```

Then list the managed libraries:

```bash
scibudy libraries
```

## Analyze a library

```bash
scibudy ingest-library <library_id>
scibudy summarize-library <library_id> --topic "calibration diagnostics"
scibudy analyze-topic <library_id> "posterior coverage"
scibudy search-evidence <library_id> "coverage diagnostic failure modes"
```

Use `--skip-forums` when you only want paper text and do not want forum or repository evidence.

## Build a cross-paper synthesis

```bash
scibudy synthesize-library <library_id> \
  "calibration in simulation-based inference" \
  --profile auto \
  --max-items 50
```

Useful profiles:

- `auto`: choose a profile from the topic.
- `general`: domain-neutral extraction.
- `sbi_calibration`: calibration-oriented method cards and risk flags.

## Search one provider

```bash
scibudy source openalex "Bayesian atmospheric chemistry inverse modeling" --limit 20
scibudy source pubmed "simulation based inference calibration" --limit 20
scibudy oa 10.1038/s41467-023-00000-0
```

## Generate a context bundle

```bash
scibudy bundle-create <library_id> --mode compact --max-items 12
scibudy bundle-show <bundle_id>
```

Use the bundle text as context for a manuscript outline, related-work section, or review response.

## Analyze journal writing style

```bash
scibudy journal-analyze \
  --journal nature-communications \
  --query "atmospheric chemistry Bayesian inference" \
  --from-year 2020 \
  --to-year 2026 \
  --target-size 100 \
  --target-dir ~/Desktop/nc-style
```

Ask Codex:

```text
Use analyze_journal_style for journal="nature-communications", query="atmospheric chemistry Bayesian inference", target_size=100, target_dir="~/Desktop/nc-style", dry_run=true. Explain the expected output files.
```

## Open the local UI

```bash
scibudy ui --open
```

The UI is best for browsing managed libraries, favoriting items, creating context bundles, reviewing reports, and changing analysis settings.

## Preflight before long automation

```bash
scibudy security-audit
scibudy doctor --install-readiness
```

Run these before asking Codex to perform multi-step writes or long ingestion jobs.
