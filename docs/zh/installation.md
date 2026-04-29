# 安装

根据你的使用方式选择安装路径。大多数用户应从 `base` profile 开始：它会安装 Python 运行时、同步 UI 资源，并可写入受管的 Codex MCP 配置。

## 前置条件

`base` profile 必需：

- Node.js 18+
- Python 3.10+
- 能访问 Python 和 npm 包源的网络

推荐：

- 需要 MCP 接入时先安装 Codex
- 源码安装时准备 Git

只有 `gpu-local` 和 `full` profile 需要 Linux、NVIDIA GPU 和 conda。

## 安装路径选择

| 路径 | 适合场景 | 命令 |
| --- | --- | --- |
| npm 安装器 | 普通用户安装 | `npx scibudy-install --profile base` |
| 源码安装 | 开发、测试本地 checkout | `python -m pip install -e .[dev]` |
| GPU local | 使用本地 Qwen embedding 和 reranker | `npx scibudy-install --profile gpu-local` |
| 开发者安装 | 需要 tests、docs、build、release 工具 | `python -m pip install -e .[dev,docs,release]` |

## 推荐 npm 安装

```bash
npx scibudy-install --profile base
scibudy doctor --json
```

安装器会根据 release manifest 安装 `scibudy==0.3.1`，同步浏览器 UI，并把运行状态放在 app home 下。它不会把生成的文献库或密钥写入源码目录。

Profiles：

- `base`：CLI、MCP 服务、UI 资源、Codex 接入。
- `analysis`：base 加分析工作流默认设置。
- `gpu-local`：base 加本地 GPU 模型环境和 warm 流程。
- `full`：所有安装层一起安装。

## 源码安装

```bash
git clone git@github.com:ONEMULE/scibudy.git
cd scibudy
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev,docs,release]
scibudy bootstrap --profile base --install-codex
scibudy doctor --json
```

当你需要运行测试、修改代码或验证未发布分支时使用源码安装。

## Codex MCP 接入

自动接入：

```bash
scibudy install-codex
codex mcp get research
```

也可以在 bootstrap 时完成：

```bash
scibudy bootstrap --profile base --install-codex
codex mcp get research
```

预期 MCP 配置使用 `stdio`，命令指向 `research-mcp` 或 `scibudy-mcp`。

## 配置密钥

缺少可选 provider key 时 Scibudy 仍可运行，但覆盖率和限额会受影响：

```bash
scibudy setup
scibudy doctor --json
```

密钥会写入 app-home `.env`，不会写入仓库。常见项包括 `OPENALEX_API_KEY`、`CROSSREF_MAILTO`、`UNPAYWALL_EMAIL`、`SEMANTIC_SCHOLAR_API_KEY`、`NCBI_API_KEY`、`CORE_API_KEY` 和 `OPENAI_API_KEY`。

## App home 与数据

默认 app home：

```text
~/.research-mcp
```

需要隔离运行时可覆盖：

```bash
export RESEARCH_MCP_HOME=/custom/path
```

搜索记录、导入的文献库元数据、生成报告、UI 资源、本地状态和 `.env` 默认都在 app home 下，除非你显式传入其他目标目录。

## 升级

npm 安装用户：

```bash
npx scibudy-install --profile base
scibudy upgrade-runtime
scibudy doctor --json
```

源码安装用户：

```bash
git pull
python -m pip install -e .[dev,docs,release]
scibudy bootstrap --profile base --install-codex
```

## 卸载或清理

如果创建过本地 GPU 环境：

```bash
scibudy uninstall-local-models --yes
```

只有在确认要删除本地 Scibudy 状态时再删除 app home：

```bash
rm -rf ~/.research-mcp
```

如果不再希望 Codex 加载 Scibudy，还需要从 `~/.codex/config.toml` 删除受管的 `research` MCP 配置块。
