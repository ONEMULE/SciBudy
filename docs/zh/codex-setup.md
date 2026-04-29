# Codex MCP 接入

Scibudy 会暴露一个名为 `research` 的本地 `stdio` MCP 服务。配置完成后，Codex 可以调用 Scibudy 的检索、建库、ingest、证据搜索、综合分析和期刊文风分析工具。

## 自动接入

使用安装器或 bootstrap：

```bash
npx scibudy-install --profile base
scibudy install-codex
codex mcp get research
```

源码 checkout 中也可以执行：

```bash
scibudy bootstrap --profile base --install-codex
codex mcp get research
```

`scibudy install-codex` 会更新：

```text
~/.codex/config.toml
```

中的受管 `research` MCP 配置块。命令会指向当前安装的 `research-mcp` 或 `scibudy-mcp`。

## 手动接入

如果不希望 Scibudy 自动修改 Codex 配置：

```bash
scibudy bootstrap --profile base --no-install-codex
```

然后在 Codex 中手动添加 `research` MCP 服务：

```text
transport: stdio
command: research-mcp
```

如果 Codex 的登录环境找不到命令，使用 `research-mcp` 的绝对路径。

## 验证

```bash
codex mcp get research
```

预期信号：

- server 名称为 `research`
- transport 为 `stdio`
- command 指向 `research-mcp` 或 `scibudy-mcp`
- 服务暴露检索、开放获取、文献库、分析、综合和 UI 工具

运行时状态检查：

```bash
scibudy doctor --json
scibudy security-audit
```

## 常用 Codex 提示词

```text
Search recent literature on posterior calibration in simulation-based inference using research_workflow. Use dry_run=true first.
```

```text
Use collect_library to build a local library for "Bayesian atmospheric chemistry inverse modeling", then ingest_library and search_library_evidence for "uncertainty calibration".
```

```text
Run analyze_journal_style for nature-communications with query "atmospheric chemistry Bayesian inference" and summarize the output files.
```

## 排查

如果 Codex 看不到 MCP：

```bash
scibudy install-codex
codex mcp get research
scibudy doctor --json
```

如果 SSH 或 GUI 启动的 Codex 找不到命令，重新运行 Scibudy 接入命令，或把 MCP 配置中的 command 改成 `research-mcp` 的绝对路径。
