# Troubleshooting

## Installer finishes but Codex does not see the MCP

Run:

```bash
scibudy install-codex
scibudy doctor
```

## Local model environment not found

Run:

```bash
scibudy install-local-models
```

## OpenAI configured but not used

Check:

```bash
scibudy analysis-settings
```

If quota or API access fails, Scibudy falls back to local retrieval where possible.

## UI not rendering

Check whether the runtime app home contains `ui/dist/index.html`.

## Provider degraded

Run:

```bash
scibudy doctor --json
```

and inspect `missing_credentials` and `suggestions`.
