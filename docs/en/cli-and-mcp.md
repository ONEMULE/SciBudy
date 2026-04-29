# CLI and MCP

Scibudy has the same research capabilities through two surfaces:

- CLI commands for shell workflows and scripts.
- A local MCP server for Codex and compatible agents.

The primary commands are `scibudy` and `scibudy-mcp`. Compatibility aliases `research-cli` and `research-mcp` remain available during `v0.x`.

## CLI command groups

| Goal | Commands |
| --- | --- |
| Setup and health | `setup`, `doctor`, `security-audit`, `bootstrap`, `install-codex`, `show-install-state`, `upgrade-runtime` |
| Search | `search`, `source`, `oa`, `providers`, `runs`, `show` |
| Build libraries | `collect`, `download`, `organize`, `import-library`, `libraries`, `library-show` |
| Analyze full text | `ingest-library`, `ingest-item`, `summarize-library`, `summarize-item`, `compare-items`, `analyze-topic`, `search-evidence` |
| Synthesize | `workflow`, `synthesize-library`, `profiles`, `analysis-reports`, `analysis-report-show` |
| Context and UI | `bundle-create`, `bundle-show`, `ui` |
| Journal style | `journal-analyze` |
| Local models | `install-local-models`, `warm-local-models`, `uninstall-local-models`, `analysis-settings`, `analysis-update` |

## Common CLI examples

```bash
scibudy doctor --json
scibudy search "simulation-based calibration" --mode general --limit 20
scibudy source openalex "Bayesian atmospheric chemistry" --limit 10
scibudy oa 10.1038/s41467-023-00000-0
scibudy collect "posterior calibration" --target-dir ~/Desktop/posterior-calibration --limit 50
scibudy ingest-library <library_id>
scibudy search-evidence <library_id> "coverage diagnostics"
scibudy synthesize-library <library_id> "simulation-based calibration" --profile auto
scibudy journal-analyze --journal nature-communications --query "atmospheric chemistry Bayesian inference" --target-dir ./nc-style
scibudy ui --open
```

## MCP tool families

The `research` MCP server exposes these main tool families:

| Tool family | Representative tools | Use when |
| --- | --- | --- |
| Search | `search_literature`, `search_biomed`, `search_source`, `resolve_open_access` | You need search results or open-access links only. |
| Agent workflow | `research_workflow` | You want one call to search, organize, ingest, and synthesize. |
| Library management | `collect_library`, `import_library`, `list_libraries`, `read_library`, `archive_library`, `restore_library`, `update_library_item` | You need persistent local libraries. |
| Ingestion and evidence | `ingest_library`, `ingest_library_item`, `search_library_evidence` | You need to search inside parsed full text. |
| Summaries and synthesis | `summarize_library`, `summarize_library_item`, `compare_library_items`, `analyze_library_topic`, `build_research_synthesis`, `list_domain_profiles` | You need structured notes or cross-paper synthesis. |
| Reports and bundles | `list_analysis_reports`, `read_analysis_report`, `read_synthesis_report`, `generate_context_bundle`, `read_context_bundle` | You need reusable context for a conversation or manuscript task. |
| Journal style | `analyze_journal_style` | You need corpus-based writing-style diagnostics for a target journal. |
| Runtime diagnostics | `health_check`, `security_check`, `get_analysis_settings`, `update_analysis_settings` | You need readiness, safety, or backend settings. |
| UI | `render_library_manager` | You want the browser or ChatGPT Apps library manager. |

## CLI to MCP mapping

| CLI | MCP |
| --- | --- |
| `scibudy search` | `search_literature` |
| `scibudy collect` | `collect_library` |
| `scibudy workflow` | `research_workflow` |
| `scibudy ingest-library` | `ingest_library` |
| `scibudy search-evidence` | `search_library_evidence` |
| `scibudy synthesize-library` | `build_research_synthesis` |
| `scibudy journal-analyze` | `analyze_journal_style` |
| `scibudy doctor` | `health_check` |
| `scibudy security-audit` | `security_check` |

Use the CLI when you want reproducible shell commands. Use MCP when Codex should choose tool arguments, inspect results, and continue the research workflow interactively.
