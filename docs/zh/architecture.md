# 架构说明

## 运行时模型

Scibudy 采用 Python 主运行时，npm 只作为跨设备安装包装层。

### 分层

- `research_mcp/`
  - MCP 服务
  - CLI
  - 文献库与目录管理
  - 分析引擎
  - 本地模型 worker client
- `web/`
  - React/Vite UI 源码
  - 构建后的静态资源
- `bin/scibudy-install.mjs`
  - 跨设备 bootstrap 安装器

## 状态模型

源码目录与用户运行时状态分离：

- 源码目录：代码、文档、工作流、示例
- app home：`.env`、状态数据库、install state、UI 资源、分析输出

## 分析链路

检索流程：

1. lexical ranking
2. dense embedding 召回
3. reranking
4. summary / report 生成

## 本地模型

高负载 GPU 模型通过独立 worker 和独立环境运行，避免影响主 CLI/MCP 运行时稳定性。
