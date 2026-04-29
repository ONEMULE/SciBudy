# 故障排查

先运行：

```bash
scibudy doctor --json
```

JSON 输出会报告 app-home 路径、provider 状态、缺少的密钥、Codex 配置状态、本地模型状态和建议步骤。

## npm 提示未登录

普通用户安装不需要 npm 登录：

```bash
npx scibudy-install --profile base
```

`npm whoami` 只和发布 installer 包有关。如果要从本机发布，运行 `npm login`；否则让 GitHub Actions 使用仓库 secrets 发布。

## Python 版本过低

Scibudy 要求 Python 3.10+：

```bash
python3 --version
```

安装新版 Python，或用受支持解释器创建虚拟环境后重新安装：

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
```

## Codex 找不到 MCP 服务

运行：

```bash
scibudy install-codex
codex mcp get research
scibudy doctor --json
```

如果 MCP 配置存在但 Codex 仍失败，把 `~/.codex/config.toml` 中的 command 改成 `research-mcp` 或 `scibudy-mcp` 的绝对路径。GUI 或 SSH login shell 的 `PATH` 与终端不同，常会导致这个问题。

## Docs Pages URL 打不开

使用精确地址：

```text
https://onemule.github.io/SciBudy/
```

其中 `SciBudy` 的大小写有影响。

## GPU local 不受支持

完整本地模型栈假设：

- Linux
- NVIDIA GPU 和可用驱动
- conda
- 足够的磁盘和显存运行 `Qwen/Qwen3-Embedding-4B` 与 `Qwen/Qwen3-Reranker-4B`

如果当前机器不满足条件，使用 `base` 或 `analysis`：

```bash
npx scibudy-install --profile base
```

## 本地模型环境不存在

运行：

```bash
scibudy install-local-models
scibudy warm-local-models --background
scibudy analysis-settings
```

如果缺少 conda 或 GPU 路径不受支持，Scibudy 仍可使用 CPU-safe 检索和 provider-backed 分析路径。

## 缺少 API key 或 provider 降级

运行：

```bash
scibudy setup
scibudy doctor --json
```

强烈推荐配置 `CROSSREF_MAILTO`、`UNPAYWALL_EMAIL` 和 `OPENALEX_API_KEY`。`SEMANTIC_SCHOLAR_API_KEY`、`NCBI_API_KEY`、`CORE_API_KEY` 和 `OPENAI_API_KEY` 是可选项，可提升覆盖率、限额或分析质量。

## OpenAI key 已配置但未使用

检查分析设置：

```bash
scibudy analysis-settings
```

如果 quota、模型权限或网络访问失败，Scibudy 会尽可能回退，并在 `doctor` 中报告降级状态。

## UI 无法打开

运行：

```bash
scibudy doctor --json
scibudy ui --open
```

如果 UI asset 检查失败，重新运行安装器或 bootstrap，让 app home 中的 `ui/dist/index.html` 刷新。

## 期刊文风 PDF 报告缺失

Markdown 和 CSV 输出不需要 PDF 工具链。可选 PDF 报告需要：

- `pandoc`
- `xelatex`

没有这些工具时，去掉 `--pdf-report`，或在本机安装相关工具。
