# Journal Text Standardization

`journal-standardize` audits an existing manuscript or note against a journal corpus that was already collected with `journal-analyze`. It builds a vocabulary from the corpus, compares ordinary prose in the input text with that vocabulary, and writes review files for out-of-corpus wording.

Use this after you have inspected the corpus and decided that it is a suitable style reference. The tool is a writing-support audit, not an automatic acceptance filter and not a source-text copier.

## Quick start

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

Preview without writing output files:

```bash
scibudy journal-standardize \
  --corpus-dir ./nc-style \
  --input ./manuscript.tex \
  --dry-run
```

## Outputs

The output directory defaults to `<corpus-dir>/standardization/<input-stem>/` and contains:

- `journal_vocabulary.csv`: corpus word counts and document counts.
- `journal_bigrams.csv` and `journal_trigrams.csv`: recurring corpus word combinations.
- `allowed_terms.txt`: technical terms excluded from ordinary-prose OOV checks.
- `oov_report.csv`: manuscript words outside the corpus after exemptions.
- `replacement_suggestions.csv`: candidate replacements for manual review.
- `standardization_summary.json`: run-level counts and paths.
- `standardized.*`: written only when `--apply --replacement-map` is used.

## Applying replacements

By default, Scibudy does not rewrite the input file. To write a standardized copy, provide a CSV replacement map:

```csv
word,replacement
customword,analysis
```

Then run:

```bash
scibudy journal-standardize \
  --corpus-dir ./nc-style \
  --input ./manuscript.tex \
  --replacement-map ./replacements.csv \
  --apply
```

The original file is never overwritten. The standardized copy is written into the output directory.

## LaTeX behavior

LaTeX mode is enabled by default. It skips commands, citations, labels, references, URLs, figure paths, table environments, bibliography content, and the title. Use `--keep-title` when the title should be audited and `--plain-text` for `.txt` or `.md` files that should not be treated as LaTeX.

## MCP use

The same behavior is available through `standardize_journal_text`. Use it when Codex should audit a manuscript against a local corpus and return generated artifact paths.

## Limits

- The audit checks vocabulary presence, not scientific correctness.
- Out-of-corpus words can be valid domain terms; add them through `--allowed-term` or `allowed_terms.txt`.
- Replacement suggestions are candidates only and require human review.
- Do not copy source article text; use corpus statistics and short recurring phrases only.
