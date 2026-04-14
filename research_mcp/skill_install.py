from __future__ import annotations

from pathlib import Path


def install_skill(target_root: Path | None = None) -> Path:
    root = target_root or (Path.home() / ".codex" / "skills" / "research-cli")
    root.mkdir(parents=True, exist_ok=True)
    skill_file = root / "SKILL.md"
    skill_file.write_text(SKILL_BODY, encoding="utf-8")
    return skill_file


SKILL_BODY = """---
name: research-cli
description: Use when you need fast academic literature search from the shell with concise outputs, library management, context bundles, local browser UI, provider diagnostics, default PDF downloading with fallback checklists, full-text ingest, evidence search, or local setup help for the Scibudy/research-mcp toolchain. Prefer this for direct search/organize/ui/analysis/bootstrap workflows instead of re-explaining commands from memory.
---

# Research CLI

Use the local `research-cli` command when the user wants scholarly search through the shell, wants provider readiness checks, or needs to configure the local research MCP on a new device.

## Quick start

- Search general literature:
  `~/.mcp/research/.venv/bin/research-cli search "test-time scaling multimodal reasoning"`
- Search one source directly:
  `~/.mcp/research/.venv/bin/research-cli source openalex "test-time scaling multimodal reasoning"`
- Biomedical search:
  `~/.mcp/research/.venv/bin/research-cli search "CRISPR off-target prediction" --mode biomed`
- Open-access lookup:
  `~/.mcp/research/.venv/bin/research-cli oa 10.1038/s41586-023-00000-0`
- Provider status:
  `~/.mcp/research/.venv/bin/research-cli providers`
- Start the local management UI:
  `~/.mcp/research/.venv/bin/research-cli ui --open`
- Search and organize into a library in one step, downloading PDFs by default and preserving manual fallback URLs:
  `~/.mcp/research/.venv/bin/research-cli collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library`
- Ingest one organized library for full-text analysis:
  `~/.mcp/research/.venv/bin/research-cli ingest-library <library_id>`
- Search chunk-level evidence inside an ingested library:
  `~/.mcp/research/.venv/bin/research-cli search-evidence <library_id> calibration`
- List persisted analysis reports:
  `~/.mcp/research/.venv/bin/research-cli analysis-reports --library-id <library_id>`
- Setup on a new machine:
  `~/.mcp/research/.venv/bin/research-cli setup --install-codex`
- Unified bootstrap:
  `~/.mcp/research/.venv/bin/scibudy bootstrap --profile base --install-codex`
- Live smoke tests:
  `~/.mcp/research/.venv/bin/research-cli doctor --smoke`

## Output formats

Use `--format table|json|markdown|titles|tsv` on search/source commands.

- `table` is the default for quick inspection
- `titles` is best for token-efficient agent output
- `json` is best for piping or post-processing
- `tsv` is best for spreadsheets or shell filters

Add `--details` when the user needs DOI/URL/PDF links.

## Run history

- Saved runs live under `~/.mcp/research/state/runs`
- List recent runs:
  `~/.mcp/research/.venv/bin/research-cli runs`
- Show the latest saved run:
  `~/.mcp/research/.venv/bin/research-cli show latest`

## Library management

- Organize a saved run into `metadata/`, `library.csv`, `library.bib`, `README.md`, downloaded PDFs when available, and a manual download checklist for misses:
  `~/.mcp/research/.venv/bin/research-cli organize --run-id latest --target-dir ~/Desktop/library`
- Organize from an existing CSV:
  `~/.mcp/research/.venv/bin/research-cli organize --csv ~/Desktop/papers.csv --target-dir ~/Desktop/library`
- Import an existing organized library into the management catalog:
  `~/.mcp/research/.venv/bin/research-cli import-library ~/Desktop/library`
- List managed libraries:
  `~/.mcp/research/.venv/bin/research-cli libraries`
- Inspect one managed library:
  `~/.mcp/research/.venv/bin/research-cli library-show <library_id>`
- Generate a compact context bundle:
  `~/.mcp/research/.venv/bin/research-cli bundle-create <library_id>`
- Re-run PDF downloads explicitly for a saved run:
  `~/.mcp/research/.venv/bin/research-cli download --run-id latest --target-dir ~/Desktop/library`

## Analysis

- Show current analysis settings:
  `~/.mcp/research/.venv/bin/research-cli analysis-settings`
- Update analysis settings:
  `~/.mcp/research/.venv/bin/research-cli analysis-update --analysis-mode hybrid --forum-source-profile high_trust`
- Summarize a library:
  `~/.mcp/research/.venv/bin/research-cli summarize-library <library_id>`
- Analyze a topic:
  `~/.mcp/research/.venv/bin/research-cli analyze-topic <library_id> calibration`
- Compare multiple items:
  `~/.mcp/research/.venv/bin/research-cli compare-items <item_id_1> <item_id_2>`
- Show one persisted report:
  `~/.mcp/research/.venv/bin/research-cli analysis-report-show <report_id>`

## Setup and troubleshooting

- Credentials are stored in `~/.mcp/research/.env`
- `setup` can prompt interactively or accept `--set KEY=VALUE`
- `install-codex` rewrites the managed `research` block in `~/.codex/config.toml`
- `providers` and `doctor` show which upstreams are ready and which credentials are missing

Prefer using the CLI directly for one-shot search tasks. Prefer the MCP tools when the model should call the integration as a structured tool inside a Codex turn.
"""
