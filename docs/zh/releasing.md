# 发布指南

## 发布前检查

1. 运行 `make test`
2. 运行 `make build-ui`
3. 运行 `make package-check`
4. 运行 `make release-check`
5. 验证安装器 smoke
6. 如果涉及本地 GPU 路径，补做 Linux GPU smoke
7. 更新 `CHANGELOG.md`
8. 检查 `release-manifest.json`

## Python 包

```bash
python -m build
```

## npm 安装器

```bash
npm pack --dry-run
```

## 版本策略

Scibudy 当前采用稳定 `v0.x` 策略。任何 breaking change 都必须写进 release notes。
