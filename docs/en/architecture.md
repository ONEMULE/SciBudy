# Architecture

## Runtime model

Scibudy is organized as a Python-first runtime with a lightweight npm bootstrap wrapper.

### Layers

- `research_mcp/`
  - MCP server
  - CLI
  - library/catalog management
  - analysis engine
  - local model worker clients
- `web/`
  - React/Vite UI source
  - built static assets
- `bin/scibudy-install.mjs`
  - bootstrap wrapper for cross-device install

## State model

Source tree and runtime state are separate:

- source tree: code, docs, workflows, examples
- app home: `.env`, state DB, install state, UI assets, analysis outputs

## Analysis model

Retrieval pipeline:

1. lexical ranking
2. dense embedding recall
3. reranking
4. summary/report generation

## Local models

Dedicated local model workers are isolated from the main runtime so that heavy GPU dependencies do not destabilize the main CLI/MCP environment.
