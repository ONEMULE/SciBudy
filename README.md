# Scibudy

Scibudy is a Codex-native scientific research expansion assistant. It provides a local `stdio` MCP server, a human-facing CLI, a browser management UI, and an optional high-quality local GPU retrieval stack.

Runtime command aliases:

- `research-mcp` / `research-cli`
- `scibudy-mcp` / `scibudy`

## First-time setup

New device flow:

```bash
npx scibudy-install --profile base
```

This creates a runtime environment, writes a local `.env`, syncs UI assets, and can update `~/.codex/config.toml`.

Developer/source install still works:

```bash
cd ~/.mcp/research
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
.venv/bin/scibudy bootstrap --profile base --install-codex
```

## Runtime layout

Scibudy uses a per-user app home by default:

- Linux/macOS default: `~/.research-mcp`
- override: `RESEARCH_MCP_HOME=/custom/path`

In source-checkout mode, it preserves legacy in-repo state when existing local markers are present.

## CLI-first usage

This project now has two front doors:

- `research-mcp`: MCP server entrypoint for Codex
- `research-cli`: shell-first command suite for humans and coding agents
- `scibudy-mcp`: MCP server alias
- `scibudy`: shell-first alias
- `research-cli ui`: local browser management UI over streamable HTTP

Examples:

```bash
~/.mcp/research/.venv/bin/research-cli search "test-time scaling multimodal reasoning" --mode general --limit 5
~/.mcp/research/.venv/bin/research-cli source openalex "test-time scaling multimodal reasoning" --format titles
~/.mcp/research/.venv/bin/research-cli oa 10.1038/s41586-023-00000-0
~/.mcp/research/.venv/bin/research-cli providers
~/.mcp/research/.venv/bin/research-cli runs
~/.mcp/research/.venv/bin/research-cli show latest --details
~/.mcp/research/.venv/bin/research-cli ui --open
~/.mcp/research/.venv/bin/research-cli install-skill
~/.mcp/research/.venv/bin/scibudy bootstrap --profile base --install-codex
```

## Tools

- `search_literature(query, mode="general", limit=10, sort="relevance")`
- `search_biomed(query, limit=10, sort="relevance")`
- `search_source(source, query, limit=10, sort="relevance")`
- `resolve_open_access(doi)`
- `health_check()`
- `download_pdfs(run_id="latest", csv_path=None, target_dir=None, limit=20)`
- `organize_library(run_id="latest", csv_path=None, target_dir=None, limit=50, download_pdfs=True)`
- `collect_library(query, mode="general", limit=20, sort="relevance", target_dir=None, download_pdfs=True)`
- `import_library(path, name=None)`
- `list_libraries(include_archived=False)`
- `read_library(library_id, include_archived_items=False)`
- `rename_library(library_id, new_name)`
- `archive_library(library_id)` / `restore_library(library_id)`
- `tag_library(library_id, tags)`
- `update_library_item(item_id, title_alias=None, notes=None, favorite=None, tags=None)`
- `archive_library_item(item_id)` / `restore_library_item(item_id)`
- `generate_context_bundle(library_id, name=None, mode="compact", max_items=12, favorites_only=False)`
- `read_context_bundle(bundle_id)`
- `render_library_manager(library_id=None, include_archived=False)`
- `get_analysis_settings()`
- `update_analysis_settings(...)`
- `ingest_library(library_id, include_forums=True, reingest=False)`
- `ingest_library_item(item_id, include_forums=True, reingest=False)`
- `summarize_library(library_id, topic=None)`
- `summarize_library_item(item_id, topic=None)`
- `compare_library_items(item_ids, topic=None)`
- `analyze_library_topic(library_id, topic)`
- `search_library_evidence(library_id, query, max_hits=8)`
- `list_analysis_reports(library_id=None, item_id=None)`
- `read_analysis_report(report_id)`

## Local commands

- `.venv/bin/research-mcp` or `.venv/bin/research-mcp serve`: run the stdio MCP server
- `.venv/bin/research-cli search ...`: run token-efficient literature search from the shell
- `.venv/bin/research-cli source ...`: search a single provider directly
- `.venv/bin/research-cli oa DOI`: resolve open-access links for a DOI
- `.venv/bin/research-cli providers`: inspect provider readiness
- `.venv/bin/research-cli runs` / `show latest`: inspect saved run history
- `.venv/bin/research-cli ui --host 127.0.0.1 --port 8765 --open`: start the local management UI
- `.venv/bin/research-cli libraries`: list managed libraries in the catalog
- `.venv/bin/research-cli library-show <library_id>`: inspect one library and its items
- `.venv/bin/research-cli bundle-create <library_id>`: generate a compact context bundle you can inject into conversation
- `.venv/bin/research-cli import-library /abs/path/to/library`: import an existing organized library into the catalog
- `.venv/bin/research-cli analysis-settings`: inspect the global analysis profile
- `.venv/bin/research-cli analysis-update --analysis-mode hybrid --compute-backend auto`: change the global analysis profile
- `.venv/bin/research-cli ingest-library <library_id>`: extract full text and optional forum evidence for a library
- `.venv/bin/research-cli summarize-library <library_id>`: build an evidence-backed library digest
- `.venv/bin/research-cli summarize-item <item_id>`: build an evidence-backed item digest
- `.venv/bin/research-cli analyze-topic <library_id> calibration`: topic-focused synthesis over ingested text
- `.venv/bin/research-cli search-evidence <library_id> calibration`: retrieve the strongest chunk/evidence matches for a topic
- `.venv/bin/research-cli analysis-reports --library-id <library_id>`: list persisted analysis reports
- `.venv/bin/research-cli analysis-report-show <report_id>`: inspect one persisted analysis report
- `.venv/bin/scibudy bootstrap --profile base|analysis|gpu-local|full`: one-shot setup/bootstrap flow
- `.venv/bin/scibudy install-local-models`: create the dedicated GPU/local-model environment
- `.venv/bin/scibudy warm-local-models --background`: warm the local embedding/reranker model caches
- `.venv/bin/scibudy uninstall-local-models --yes`: remove the dedicated local-model environment
- `.venv/bin/scibudy show-install-state`: inspect persisted install/bootstrap state
- `.venv/bin/scibudy upgrade-runtime --spec scibudy==0.1.0`: upgrade the installed Python runtime package
- `.venv/bin/research-cli download --run-id latest --target-dir ~/Desktop/library`: download PDFs from a saved run when you explicitly want local copies
- `.venv/bin/research-cli organize --run-id latest --target-dir ~/Desktop/library`: create an organized local library with metadata, CSV, Markdown, BibTeX, automatic PDF downloads when available, and a manual download checklist for misses
- `.venv/bin/research-cli collect "query" --target-dir ~/Desktop/library`: search and organize in one step; by default it downloads PDFs when available and still keeps fallback checklist data
- `.venv/bin/research-cli install-skill`: install a Codex skill that teaches the agent how to use the CLI
- `.venv/bin/research-mcp setup --install-codex`: collect credentials and register the Codex config block
- `.venv/bin/research-mcp doctor --smoke`: inspect readiness and run lightweight live provider checks
- `.venv/bin/research-mcp install-codex`: install or refresh the managed `research` block in `~/.codex/config.toml`

## Credentials

The server works without some credentials, but long-term production use is better with:

- `OPENALEX_API_KEY`
- `CROSSREF_MAILTO`
- `SEMANTIC_SCHOLAR_API_KEY`
- `NCBI_API_KEY`
- `UNPAYWALL_EMAIL`
- `CORE_API_KEY`

`SEMANTIC_SCHOLAR_API_KEY`, `UNPAYWALL_EMAIL`, and `CORE_API_KEY` are treated as required for those specific providers. Missing values cause the provider to be skipped instead of failing the whole search.

Semantic Scholar also supports a best-effort public mode when no API key is present. In that mode this project uses the public `paper/search/bulk` path, which is lower throughput and less stable than authenticated access.

## Context bundles and UI

The management layer now supports:

- a local browser UI over `streamable-http`
- a ChatGPT Apps-compatible widget resource
- managed libraries and item-level safe mutations
- compact context bundles for efficient conversation injection
- MCP `resources` and `prompts` for loading existing library context without dumping raw libraries into the transcript

The analysis layer now adds:

- full-text extraction from local/remote PDF and HTML sources
- chunking and local chunk storage
- a highest-quality local embedding path via `Qwen/Qwen3-Embedding-4B` plus `Qwen/Qwen3-Reranker-4B` in a dedicated `research_embed` conda environment
- optional forum/review enrichment
- configurable analysis modes: `rules`, `hybrid`, `semantic_heavy`
- configurable compute backends: `local`, `openai`, `auto`
- item/library/topic-level summaries
- evidence search over ingested chunk text
- persisted analysis reports with report ids and file paths

The distribution layer now adds:

- a unified npm installer: `scibudy-install`
- a persisted install-state record under the app home
- profile-based bootstrap: `base`, `analysis`, `gpu-local`, `full`
- dedicated local-model env management for the `qwen4b` profile

## Codex config

The preferred path is to let `research-mcp install-codex` manage the `research` block in `~/.codex/config.toml`. The managed block uses the local console script and keeps only non-secret settings in Codex config.

```toml
[mcp_servers.research]
command = "/home/USER/.mcp/research/.venv/bin/research-mcp"
args = []
cwd = "/home/USER/.mcp/research"
enabled = true
required = false
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled_tools = [
  "search_literature",
  "search_biomed",
  "search_source",
  "resolve_open_access",
  "health_check",
  "download_pdfs",
  "organize_library",
  "collect_library",
  "import_library",
  "list_libraries",
  "read_library",
  "rename_library",
  "archive_library",
  "restore_library",
  "tag_library",
  "update_library_item",
  "archive_library_item",
  "restore_library_item",
  "generate_context_bundle",
  "read_context_bundle",
  "render_library_manager",
]
env_vars = [
  "OPENALEX_API_KEY",
  "CROSSREF_MAILTO",
  "SEMANTIC_SCHOLAR_API_KEY",
  "NCBI_API_KEY",
  "UNPAYWALL_EMAIL",
  "CORE_API_KEY",
]

[mcp_servers.research.env]
RESEARCH_MCP_CACHE_DB_PATH = "/home/onemule/.mcp/research/state/research.db"
RESEARCH_MCP_ENABLE_DOAJ = "true"
RESEARCH_MCP_ENABLE_CORE = "true"
RESEARCH_MCP_ENABLE_SEMANTIC_SCHOLAR = "true"
RESEARCH_MCP_ALLOW_PUBLIC_SEMANTIC_SCHOLAR = "true"
RESEARCH_MCP_LOG_LEVEL = "ERROR"
```
