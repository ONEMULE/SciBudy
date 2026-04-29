# Journal Style Analysis

Scibudy can build a target-journal corpus and produce structural writing diagnostics. The workflow collects article metadata, fetches article pages, optionally downloads PDFs, parses sections, captions, references, and sentence patterns, then writes CSV files plus a Markdown report.

Use this for manuscript preparation when you want to understand how a journal tends to structure articles. Do not use it to copy article text, bypass copyright, or replace the journal's official author instructions.

## Inputs

Required:

- `--journal`: built-in journal preset, for example `nature-communications` or `npj-cas`.
- `--target-dir`: output directory.

Recommended:

- `--query`: project-adjacent topic used to prioritize the corpus.
- `--from-year` and `--to-year`: publication window.
- `--target-size`: target number of articles.

Optional:

- `--skip-pdfs`: parse pages and metadata without downloading PDFs.
- `--pdf-report`: render the report to PDF when local dependencies exist.
- `--dry-run`: show planned writes without creating files.

## Quick start

```bash
scibudy journal-analyze \
  --journal nature-communications \
  --query "atmospheric chemistry Bayesian inference" \
  --from-year 2020 \
  --to-year 2026 \
  --target-size 100 \
  --target-dir ./nc-style
```

Preview only:

```bash
scibudy journal-analyze --journal nature-communications --target-dir ./nc-style --dry-run
```

Generate a PDF report when `pandoc` and `xelatex` are available:

```bash
scibudy journal-analyze --journal nature-communications --target-dir ./nc-style --pdf-report
```

## Outputs

The target directory contains:

- `data/corpus_manifest.csv`: selected article list and parser status.
- `data/candidate_pool_raw.csv`: raw Crossref candidate pool.
- `data/selection_scores.csv`: domain and method relevance scores.
- `data/manual_download_checklist.csv`: PDFs that need manual follow-up.
- `data/citation_matrix.csv`: reference count and citation-density metrics.
- `analysis/section_stats.csv`: section word counts.
- `analysis/sentence_stats.csv`: sentence-length data.
- `analysis/caption_stats.csv`: display item and caption metrics.
- `analysis/phrase_bank.csv`: recurring verbs, hedge terms, and phrase fragments.
- `analysis/summary_metrics.json`: compact run-level metrics.
- `report/journal_style_report.md`: writing guidance and summary statistics.
- `report/journal_style_report.pdf`: optional rendered report.

## Recommended workflow

1. Run `--dry-run` first and confirm the target directory.
2. Use a topic query close to your manuscript instead of the whole journal.
3. Inspect `corpus_manifest.csv` for parser failures and irrelevant articles.
4. Use the Markdown report as style guidance, not as source text.
5. Compare findings against the journal's official author instructions before changing a manuscript.

## Built-in presets

- `nature-communications`: Nature Communications article patterns.
- `npj-cas`: npj Climate and Atmospheric Science article patterns.

## Limits

- Metadata and full-text availability depend on publisher pages, open-access links, and network access.
- PDF download is best-effort; inaccessible PDFs remain unavailable.
- PDF report generation requires local `pandoc` and `xelatex`; Markdown and CSV outputs are still produced without them.
- Reported phrases are statistical style signals and must not be copied as article text.
- This feature does not guarantee acceptance at any journal.

## Copyright boundary

Scibudy reports corpus-level structure, counts, and short recurring phrase fragments for analysis. Keep full article PDFs and extracted text in your local workspace, respect publisher licenses, and quote or paraphrase source articles according to your institution's rules.
