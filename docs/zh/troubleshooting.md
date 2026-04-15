# 故障排查

## Codex 看不到 MCP

```bash
scibudy install-codex
scibudy doctor
```

## 本地模型环境不存在

```bash
scibudy install-local-models
```

## OpenAI 已配置但没有被使用

```bash
scibudy analysis-settings
```

如果 OpenAI 配额或权限不可用，系统会按设计回退到本地路径。

## UI 无法打开

检查 app home 下是否存在 `ui/dist/index.html`。

## Provider 异常

```bash
scibudy doctor --json
```

重点查看 `missing_credentials` 和 `suggestions`。
