# 使用示例

下面的示例是可复制的任务模板。把 topic、路径和 ID 换成你自己的值即可。

## 让 Codex 帮我收集文献

在 `scibudy install-codex` 和 `codex mcp get research` 成功后使用：

```text
Use research_workflow with query="calibration methods in simulation-based inference", mode="general", limit=50, dry_run=true. Show me the planned writes before creating a library.
```

确认计划后：

```text
Run the same research_workflow without dry_run. Use target_dir="~/Desktop/sbc-calibration-library", ingest=true, synthesize=true, topic="calibration in simulation-based inference", profile="auto".
```

## 用 CLI 建立文献库

```bash
scibudy collect "calibration methods in simulation-based inference" \
  --mode general \
  --limit 50 \
  --target-dir ~/Desktop/sbc-calibration-library \
  --name "SBI calibration library"
```

然后查看受管文献库：

```bash
scibudy libraries
```

## 分析文献库

```bash
scibudy ingest-library <library_id>
scibudy summarize-library <library_id> --topic "calibration diagnostics"
scibudy analyze-topic <library_id> "posterior coverage"
scibudy search-evidence <library_id> "coverage diagnostic failure modes"
```

只想分析论文全文、不需要论坛或仓库证据时，加 `--skip-forums`。

## 做跨论文综合

```bash
scibudy synthesize-library <library_id> \
  "calibration in simulation-based inference" \
  --profile auto \
  --max-items 50
```

常用 profile：

- `auto`：根据 topic 自动选择。
- `general`：通用领域提取。
- `sbi_calibration`：偏校准方法卡和风险标记。

## 搜索单个 provider

```bash
scibudy source openalex "Bayesian atmospheric chemistry inverse modeling" --limit 20
scibudy source pubmed "simulation based inference calibration" --limit 20
scibudy oa 10.1038/s41467-023-00000-0
```

## 生成 context bundle

```bash
scibudy bundle-create <library_id> --mode compact --max-items 12
scibudy bundle-show <bundle_id>
```

Bundle 文本适合作为论文大纲、related work 或审稿回复的上下文。

## 做期刊文风分析

```bash
scibudy journal-analyze \
  --journal nature-communications \
  --query "atmospheric chemistry Bayesian inference" \
  --from-year 2020 \
  --to-year 2026 \
  --target-size 100 \
  --target-dir ~/Desktop/nc-style
```

给 Codex 的提示词：

```text
Use analyze_journal_style for journal="nature-communications", query="atmospheric chemistry Bayesian inference", target_size=100, target_dir="~/Desktop/nc-style", dry_run=true. Explain the expected output files.
```

## 打开本地 UI

```bash
scibudy ui --open
```

UI 适合浏览受管文献库、收藏条目、创建 context bundle、查看报告和调整分析设置。

## 长任务前的预检

```bash
scibudy security-audit
scibudy doctor --install-readiness
```

在让 Codex 执行多步骤写入或长时间 ingest 前先运行这些检查。
