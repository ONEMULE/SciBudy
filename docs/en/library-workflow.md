# Library Workflow

## Search to library

```bash
scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library
```

## Import an existing library

```bash
scibudy import-library /abs/path/to/library
```

## Analyze

```bash
scibudy ingest-library <library_id>
scibudy summarize-library <library_id>
scibudy analyze-topic <library_id> calibration
```

## Reports

```bash
scibudy analysis-reports --library-id <library_id>
scibudy analysis-report-show <report_id>
```

## Journal style analysis

```bash
scibudy journal-analyze --journal nature-communications --query "atmospheric chemistry Bayesian inference" --target-dir ./nc-style
```

Use this when the goal is to learn a target journal's writing patterns rather than synthesize evidence for a specific scientific claim.

## Context bundles

```bash
scibudy bundle-create <library_id>
```
