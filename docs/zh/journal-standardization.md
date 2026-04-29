# 期刊文本标准化

`journal-standardize` 用已有的目标期刊语料来审计一份手稿或笔记。它会从 `journal-analyze` 已收集的语料中建立词表，把输入文本中的普通叙述词与该词表比较，并输出不在语料中的词汇报告。

这个功能适合在完成目标期刊语料收集和人工检查后使用。它是写作辅助审计，不是自动录用判断，也不是复制期刊原文的工具。

## 快速开始

```bash
scibudy journal-analyze \
  --journal nature-communications \
  --query "atmospheric chemistry Bayesian inference" \
  --target-dir ./nc-style \
  --target-size 100

scibudy journal-standardize \
  --corpus-dir ./nc-style \
  --input ./manuscript.tex
```

只预览，不写文件：

```bash
scibudy journal-standardize \
  --corpus-dir ./nc-style \
  --input ./manuscript.tex \
  --dry-run
```

## 输出内容

默认输出目录是 `<corpus-dir>/standardization/<input-stem>/`，包含：

- `journal_vocabulary.csv`：语料词频和文档频次。
- `journal_bigrams.csv` 和 `journal_trigrams.csv`：常见词组。
- `allowed_terms.txt`：从普通叙述词检查中排除的专业术语。
- `oov_report.csv`：豁免后仍不在语料中的文本词汇。
- `replacement_suggestions.csv`：供人工检查的替换候选。
- `standardization_summary.json`：运行摘要。
- `standardized.*`：只有使用 `--apply --replacement-map` 时才生成。

## 应用替换

默认不会改写输入文件。若要生成标准化副本，需要提供 replacement map：

```csv
word,replacement
customword,analysis
```

然后运行：

```bash
scibudy journal-standardize \
  --corpus-dir ./nc-style \
  --input ./manuscript.tex \
  --replacement-map ./replacements.csv \
  --apply
```

原文件不会被覆盖。标准化副本会写入输出目录。

## LaTeX 行为

默认启用 LaTeX 模式，会跳过命令、引用、标签、交叉引用、URL、图片路径、表格环境、参考文献和标题。需要检查标题时使用 `--keep-title`；如果输入是普通 `.txt` 或 `.md`，可用 `--plain-text`。

## MCP 使用

同一能力通过 `standardize_journal_text` 暴露给 MCP。适合让 Codex 对本地手稿执行语料化审计并返回输出路径。

## 限制

- 该审计检查词汇是否出现在语料中，不判断科学内容是否正确。
- 不在语料中的词可能是合理专业术语，可用 `--allowed-term` 或 `allowed_terms.txt` 加入豁免。
- 替换建议只是候选，需要人工确认。
- 不要复制来源文章原文；只使用语料统计和短语层面的风格信号。
