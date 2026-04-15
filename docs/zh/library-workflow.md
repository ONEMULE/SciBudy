# 文献库工作流

## 从检索到文献库

```bash
scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library
```

## 导入已有文献库

```bash
scibudy import-library /abs/path/to/library
```

## 分析

```bash
scibudy ingest-library <library_id>
scibudy summarize-library <library_id>
scibudy analyze-topic <library_id> calibration
```

## 报告

```bash
scibudy analysis-reports --library-id <library_id>
scibudy analysis-report-show <report_id>
```

## 上下文包

```bash
scibudy bundle-create <library_id>
```
