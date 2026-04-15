# Installation

## Recommended path

Use the npm bootstrap wrapper:

```bash
npx scibudy-install --profile base
```

## Profiles

- `base`: MCP server, CLI, UI, Codex config
- `analysis`: analysis-oriented runtime defaults
- `gpu-local`: dedicated local-model environment
- `full`: all of the above

## Source install

```bash
git clone git@github.com:ONEMULE/scibudy.git
cd scibudy
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
scibudy bootstrap --profile base --install-codex
```

## Platform support

- Linux: first-class support
- macOS: supported for base + analysis
- Windows: not first-class in `v0.x`

## App home

Default app home:

- Linux/macOS: `~/.research-mcp`

Override with:

```bash
export RESEARCH_MCP_HOME=/custom/path
```
