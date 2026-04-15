# GPU Local Models

## Supported path

Full local high-quality semantic retrieval is Linux-first and currently assumes:

- NVIDIA GPU
- conda available
- dedicated env: `research_embed`

## Install

```bash
scibudy install-local-models
```

## Warm model caches

```bash
scibudy warm-local-models --background
```

## Current local model profile

- embedding: `Qwen/Qwen3-Embedding-4B`
- reranker: `Qwen/Qwen3-Reranker-4B`

## Validation

```bash
scibudy analysis-settings
scibudy ingest-item <item_id> --reingest --skip-forums
scibudy search-evidence <library_id> calibration --format json
```

Expected signal:

- `compute_backend: local_transformer`
- `semantic_backend: local_transformer+reranker`
