# 快速开始

## 1. 初始化

```bash
npx scibudy-install --profile base
```

## 2. 查看健康状态

```bash
scibudy doctor --json
```

## 3. 搜索文献

```bash
scibudy search "simulation-based calibration"
```

## 4. 建立文献库

```bash
scibudy collect "simulation-based calibration" --target-dir ~/Desktop/sbc-library
```

## 5. 分析文献库

```bash
scibudy ingest-library <library_id>
scibudy analyze-topic <library_id> calibration
```

## 6. 打开界面

```bash
scibudy ui --open
```
