# 快速开始

这条路径假设机器上已有 Node.js 18+ 和 Python 3.10+。它会安装 base 运行时、验证安装、接入 Codex、执行检索、建立文献库，并打开本地 UI。

## 1. 安装 base 运行时

```bash
npx scibudy-install --profile base
```

安装器会创建或更新 Scibudy 运行时，并把本地状态放在 app home，通常是 `~/.research-mcp`。

## 2. 验证安装

```bash
scibudy doctor --json
```

优先查看：

- `status`：整体状态。
- `app_home`：Scibudy 本地状态目录。
- `provider_statuses`：各检索 provider 是否可用。
- `missing_credentials`：哪些可选 key 可以提升覆盖率。
- `codex_configured`：Codex 是否已有受管 MCP 配置。

## 3. 接入 Codex

```bash
scibudy install-codex
codex mcp get research
```

你应看到名为 `research` 的 `stdio` MCP 服务。如果当前机器没有安装 Codex，可以跳过这一步，直接使用 CLI。

## 4. 第一次检索

```bash
scibudy search "simulation-based calibration" --limit 10
```

生物医学检索可用 `--mode biomed`；需要优先最新结果时使用 `--sort recent`。

## 5. 建立本地文献库

```bash
scibudy collect "simulation-based calibration" \
  --target-dir ~/Desktop/sbc-library \
  --limit 30
```

该命令会写入整理后的 metadata、Markdown、BibTeX，并在可获得开放 PDF 时下载。付费或不可获取的 PDF 会进入人工下载清单，不会伪造全文。

## 6. Ingest 并分析文献库

```bash
scibudy libraries
scibudy ingest-library <library_id>
scibudy analyze-topic <library_id> calibration
scibudy search-evidence <library_id> "posterior coverage"
```

`library_id` 可从 `scibudy libraries` 或 collect 命令返回结果中获取。

## 7. 打开 UI

```bash
scibudy ui --open
```

UI 是本地浏览器管理界面，用于管理文献库、条目、分析设置、context bundle 和生成报告。

## 8. 让 Codex 调用工作流

完成 MCP 接入后，可以使用类似提示词：

```text
Use research_workflow with query="calibration methods in simulation-based inference", mode="general", limit=50, synthesize=true.
```

为了更安全地自动化，先要求 `dry_run=true`，或用 `quality_mode=fast` 做低成本检索和建库。
