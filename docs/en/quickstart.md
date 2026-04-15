# Quickstart

## 1. Bootstrap

```bash
npx scibudy-install --profile base
```

## 2. Check health

```bash
scibudy doctor --json
```

## 3. Search literature

```bash
scibudy search "simulation-based calibration"
```

## 4. Build a library

```bash
scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library
```

## 5. Analyze a library

```bash
scibudy ingest-library <library_id>
scibudy analyze-topic <library_id> calibration
```

## 6. Open the UI

```bash
scibudy ui --open
```
