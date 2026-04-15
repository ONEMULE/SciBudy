# Releasing

## Release checklist

1. Run `make test`
2. Run `make build-ui`
3. Run `make package-check`
4. Run `make release-check`
5. Validate installer smoke
6. Validate Linux GPU local-model smoke if the release touches that path
7. Update `CHANGELOG.md`
8. Verify `release-manifest.json`

## Python package

Build:

```bash
python -m build
```

## npm installer

Check:

```bash
npm pack --dry-run
```

## Release intent

Scibudy uses a stable `v0.x` policy. Any breaking change must be called out in the release notes.
