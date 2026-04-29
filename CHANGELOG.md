# Changelog

All notable changes to Scibudy are documented in this file.

The project follows a pragmatic `v0.x` stability model:

- core interfaces are intended to be usable and documented
- breaking changes may still happen when they materially improve architecture or install reliability
- release notes must call out any breaking change explicitly

## [0.3.1] - 2026-04-29

### Added
- `journal-standardize` CLI and `standardize_journal_text` MCP tool for auditing existing text against a collected journal corpus.
- Corpus-derived vocabulary, bigram, trigram, allowed-term, OOV, replacement-suggestion, and summary outputs for journal text standardization.
- Bilingual documentation for the journal text standardization flow.

### Changed
- Journal style documentation now links the `journal-analyze` corpus-building step to the new standardization audit step.

### Validation
- Added deterministic tests for dry-run behavior, allowed-term handling, replacement-map application, and CLI JSON output.

## [0.3.0] - 2026-04-29

### Added
- User-facing README, Docs Pages, and release-entry documentation for install, quickstart, Codex MCP setup, CLI/MCP mapping, examples, troubleshooting, and journal-style analysis.
- Journal-style analysis documentation covering inputs, outputs, PDF-report dependencies, copyright boundaries, and recommended usage.

### Changed
- Package homepage and documentation URLs now point to the public Docs Pages site at `https://onemule.github.io/SciBudy/`.
- npm and PyPI package descriptions now use the same public product description.

### Validation
- Release checks cover tests, compileall, strict MkDocs build, npm dry-run packaging, release manifest consistency, and smoke install.

## [0.1.0] - 2026-04-14

### Added
- Codex/MCP scholarly search and research-library management runtime
- browser management UI
- unified npm bootstrap installer
- install-state tracking and runtime/app-home separation
- local GPU semantic retrieval path with Qwen embedding + reranker workers
- bilingual repo-native documentation skeleton
- professional open-source governance and release scaffolding
