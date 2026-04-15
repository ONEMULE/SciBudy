# Configuration

## Secrets

User secrets live in the app-home `.env` file.

Common variables:

- `OPENALEX_API_KEY`
- `CROSSREF_MAILTO`
- `SEMANTIC_SCHOLAR_API_KEY`
- `NCBI_API_KEY`
- `UNPAYWALL_EMAIL`
- `CORE_API_KEY`
- `OPENAI_API_KEY`

## Analysis configuration

Use:

```bash
scibudy analysis-settings
scibudy analysis-update --analysis-mode hybrid --compute-backend local
```

Important analysis settings:

- `analysis_mode`
- `compute_backend`
- `chunk_size`
- `chunk_overlap`
- `forum_source_profile`
- local embedding/reranker model settings

## Runtime state

The app home stores:

- `.env`
- `state/`
- `analysis/`
- `library/`
- `ui/dist/`
