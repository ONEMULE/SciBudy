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

## 发布配置

### PyPI

支持两种方式：

- GitHub OIDC trusted publishing
- 通过 `PYPI_API_TOKEN` 进行 token 发布

仓库变量：

- `PYPI_TRUSTED_PUBLISHING_ENABLED=true`

如果 trusted publishing 和 `PYPI_API_TOKEN` 都没有配置，PyPI 发布工作流会自动跳过，不会直接报红。

### npm

需要仓库 secret：

- `NPM_TOKEN`

如果 `NPM_TOKEN` 不存在，npm 发布工作流会自动跳过。

## 版本策略

Scibudy 当前采用稳定 `v0.x` 策略。任何 breaking change 都必须写进 release notes。
