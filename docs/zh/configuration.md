# 配置说明

## 密钥

用户密钥保存在 app home 的 `.env` 文件中。

常见变量：

- `OPENALEX_API_KEY`
- `CROSSREF_MAILTO`
- `SEMANTIC_SCHOLAR_API_KEY`
- `NCBI_API_KEY`
- `UNPAYWALL_EMAIL`
- `CORE_API_KEY`
- `OPENAI_API_KEY`

## 分析配置

```bash
scibudy analysis-settings
scibudy analysis-update --analysis-mode hybrid --compute-backend local
```

重要项：

- `analysis_mode`
- `compute_backend`
- `chunk_size`
- `chunk_overlap`
- `forum_source_profile`
- 本地 embedding / reranker 配置

## 运行目录

app home 中默认包括：

- `.env`
- `state/`
- `analysis/`
- `library/`
- `ui/dist/`
