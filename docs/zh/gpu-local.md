# 本地 GPU 模型

## 支持路径

当前高质量本地语义检索路径优先支持：

- Linux
- NVIDIA GPU
- conda 环境

## 安装

```bash
scibudy install-local-models
```

## 预热模型

```bash
scibudy warm-local-models --background
```

## 当前本地模型 profile

- embedding：`Qwen/Qwen3-Embedding-4B`
- reranker：`Qwen/Qwen3-Reranker-4B`

## 验证

```bash
scibudy ingest-item <item_id> --reingest --skip-forums
scibudy search-evidence <library_id> calibration --format json
```

期望看到：

- `compute_backend: local_transformer`
- `semantic_backend: local_transformer+reranker`
