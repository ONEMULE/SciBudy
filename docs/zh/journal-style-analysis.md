# 期刊文风分析

Scibudy 可以为目标期刊建立语料库，并输出结构化写作诊断。流程会收集文章元数据，抓取文章页面，可选下载 PDF，解析章节、图注、参考文献和句式模式，然后生成 CSV 文件和 Markdown 报告。

这个能力适合论文写作准备，用来理解目标期刊常见的文章结构。不要用它复制论文原文、绕过版权，也不要用它替代期刊官方 author instructions。

## 输入

必需：

- `--journal`：内置期刊 preset，例如 `nature-communications` 或 `npj-cas`。
- `--target-dir`：输出目录。

推荐：

- `--query`：与项目接近的主题，用于筛选语料。
- `--from-year` 和 `--to-year`：发表年份范围。
- `--target-size`：目标文章数量。

可选：

- `--skip-pdfs`：不下载 PDF，只解析页面和元数据。
- `--pdf-report`：本机依赖可用时渲染 PDF 报告。
- `--dry-run`：只显示计划写入内容，不创建文件。

## 快速开始

```bash
scibudy journal-analyze \
  --journal nature-communications \
  --query "atmospheric chemistry Bayesian inference" \
  --from-year 2020 \
  --to-year 2026 \
  --target-size 100 \
  --target-dir ./nc-style
```

只预览：

```bash
scibudy journal-analyze --journal nature-communications --target-dir ./nc-style --dry-run
```

如果本机有 `pandoc` 和 `xelatex`，可生成 PDF 报告：

```bash
scibudy journal-analyze --journal nature-communications --target-dir ./nc-style --pdf-report
```

## 输出内容

目标目录包含：

- `data/corpus_manifest.csv`：最终文章清单和解析状态。
- `data/candidate_pool_raw.csv`：Crossref 原始候选池。
- `data/selection_scores.csv`：领域和方法相似度评分。
- `data/manual_download_checklist.csv`：需要人工跟进的 PDF。
- `data/citation_matrix.csv`：参考文献数量和引用密度。
- `analysis/section_stats.csv`：章节词数。
- `analysis/sentence_stats.csv`：句长数据。
- `analysis/caption_stats.csv`：图表和图注指标。
- `analysis/phrase_bank.csv`：常见动词、缓和词和短语片段。
- `analysis/summary_metrics.json`：运行级摘要指标。
- `report/journal_style_report.md`：写作建议和统计摘要。
- `report/journal_style_report.pdf`：可选渲染报告。

## 推荐使用方式

1. 先运行 `--dry-run`，确认目标目录。
2. 使用贴近当前论文的 topic query，不要直接分析整个期刊。
3. 检查 `corpus_manifest.csv`，排除解析失败或明显无关的文章。
4. 把 Markdown 报告当作风格参考，不要当作可复制文本。
5. 修改稿件前，对照目标期刊官方 author instructions。

## 内置期刊

- `nature-communications`：Nature Communications 文章模式。
- `npj-cas`：npj Climate and Atmospheric Science 文章模式。

## 限制

- 元数据和全文可用性取决于出版社页面、开放获取链接和网络状态。
- PDF 下载是 best-effort；不可访问的 PDF 不会被伪造。
- PDF 报告依赖本机 `pandoc` 和 `xelatex`；没有它们时仍会生成 Markdown 和 CSV。
- 报告中的短语是统计风格信号，不能当作论文原文复制。
- 该功能不保证任何期刊录用。

## 版权边界

Scibudy 输出的是语料层面的结构、计数和短语片段分析。请把全文 PDF 和解析文本保留在本地工作区，遵守出版社许可，并按机构规范引用或转述来源文章。
