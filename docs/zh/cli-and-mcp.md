# CLI 与 MCP

Scibudy 通过两个入口提供同一套科研能力：

- CLI 命令，适合 shell 工作流和脚本。
- 本地 MCP 服务，适合 Codex 和兼容 agent 调用。

主命令是 `scibudy` 和 `scibudy-mcp`。兼容别名 `research-cli` 和 `research-mcp` 在 `v0.x` 阶段继续保留。

## CLI 命令分组

| 目标 | 命令 |
| --- | --- |
| 安装与健康检查 | `setup`, `doctor`, `security-audit`, `bootstrap`, `install-codex`, `show-install-state`, `upgrade-runtime` |
| 检索 | `search`, `source`, `oa`, `providers`, `runs`, `show` |
| 建库 | `collect`, `download`, `organize`, `import-library`, `libraries`, `library-show` |
| 全文分析 | `ingest-library`, `ingest-item`, `summarize-library`, `summarize-item`, `compare-items`, `analyze-topic`, `search-evidence` |
| 综合分析 | `workflow`, `synthesize-library`, `profiles`, `analysis-reports`, `analysis-report-show` |
| Context 与 UI | `bundle-create`, `bundle-show`, `ui` |
| 期刊文风 | `journal-analyze` |
| 本地模型 | `install-local-models`, `warm-local-models`, `uninstall-local-models`, `analysis-settings`, `analysis-update` |

## 常用 CLI 示例

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

## MCP 工具族

`research` MCP 服务暴露以下主要工具族：

| 工具族 | 代表工具 | 适合场景 |
| --- | --- | --- |
| 检索 | `search_literature`, `search_biomed`, `search_source`, `resolve_open_access` | 只需要检索结果或开放获取链接。 |
| Agent 工作流 | `research_workflow` | 希望一次完成检索、建库、ingest 和 synthesis。 |
| 文献库管理 | `collect_library`, `import_library`, `list_libraries`, `read_library`, `archive_library`, `restore_library`, `update_library_item` | 需要持久化本地文献库。 |
| Ingestion 与证据 | `ingest_library`, `ingest_library_item`, `search_library_evidence` | 需要在解析后的全文中搜索。 |
| 总结与综合 | `summarize_library`, `summarize_library_item`, `compare_library_items`, `analyze_library_topic`, `build_research_synthesis`, `list_domain_profiles` | 需要结构化笔记或跨论文综合。 |
| 报告与 context | `list_analysis_reports`, `read_analysis_report`, `read_synthesis_report`, `generate_context_bundle`, `read_context_bundle` | 需要可复用的对话或写作上下文。 |
| 期刊文风 | `analyze_journal_style` | 需要目标期刊的语料化写作风格诊断。 |
| 运行时诊断 | `health_check`, `security_check`, `get_analysis_settings`, `update_analysis_settings` | 需要检查准备状态、安全性或后端设置。 |
| UI | `render_library_manager` | 需要浏览器或 ChatGPT Apps 文献库管理界面。 |

## CLI 与 MCP 对应关系

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

需要可复现 shell 命令时用 CLI；需要 Codex 自动选择参数、阅读结果并继续研究流程时用 MCP。
