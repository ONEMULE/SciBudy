# Scibudy

Scibudy is a Codex-native scientific research assistant for scholarly search, paper-library management, full-text analysis, local evidence search, and journal-style diagnostics.

Scibudy 提供面向 Codex 的学术检索、文献库管理、全文分析、本地证据检索与期刊文风分析能力。

## Choose your language

- [English documentation](en/index.md)
- [中文文档](zh/index.md)

## Quick start

```bash
npx scibudy-install --profile base
scibudy doctor --json
scibudy install-codex
codex mcp get research
scibudy search "simulation-based calibration"
scibudy ui --open
```

## Release and packages

- GitHub Releases: <https://github.com/ONEMULE/scibudy/releases>
- npm installer: <https://www.npmjs.com/package/scibudy-installer>
- PyPI package: <https://pypi.org/project/scibudy/>

## Local GPU option

For Linux + NVIDIA systems:

```bash
scibudy install-local-models
scibudy warm-local-models --background
```
