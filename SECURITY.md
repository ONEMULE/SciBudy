# Security Policy

## Supported versions

Security fixes are applied to the latest `main` branch and the latest published `v0.x` release line.

## Report a vulnerability

Do not open public GitHub issues for:

- credential leaks
- unsafe local execution paths
- installer privilege escalation
- secrets/config exposure
- remote code execution risks

Instead, report privately to the maintainer before public disclosure.

Until a dedicated security email is established, use GitHub private security reporting if enabled, or contact the maintainer directly through the repository owner account.

## Scope

Security-sensitive areas include:

- `.env` and secret handling
- Codex config generation
- installer/runtime path handling
- local model worker process management
- any network-facing MCP or HTTP interfaces
