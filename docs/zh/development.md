# 开发指南

## 工具层

- Python 运行时：`.venv`
- 前端：`web/`
- npm 安装器：`bin/`

## 常用命令

```bash
make verify-local
```

普通改动运行 `make verify-local`。如果改动涉及 Pages、安装器、包元数据或
release manifest，再运行：

```bash
make verify-full
```

## 开发原则

- 公共 CLI/MCP 行为要明确
- 安装层和运行层要分离
- 不提交用户状态、日志或密钥
- 公共行为变化必须同步更新文档
