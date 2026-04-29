from __future__ import annotations

import csv
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import time
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from research_mcp.journal_profiles import JournalProfile, get_journal_profile
from research_mcp.models import JournalStyleAnalysisResponse
from research_mcp.paths import APP_HOME
from research_mcp.settings import Settings
from research_mcp.utils import now_utc_iso


CLAIM_VERBS = (
    "show",
    "demonstrate",
    "reveal",
    "indicate",
    "suggest",
    "estimate",
    "quantify",
    "constrain",
    "identify",
    "attribute",
    "resolve",
    "improve",
    "predict",
    "explain",
)

HEDGE_WORDS = (
    "may",
    "might",
    "could",
    "likely",
    "suggest",
    "potential",
    "approximately",
    "consistent",
    "uncertain",
)

STOP_SECTION_TITLES = {
    "References",
    "Acknowledgements",
    "Acknowledgments",
    "Funding",
    "Author information",
    "Ethics declarations",
    "Additional information",
    "Supplementary information",
    "Source data",
    "Rights and permissions",
    "About this article",
    "Peer review",
    "Competing interests",
    "Reporting summary",
}

CANONICAL_SECTIONS = {
    "Abstract": "abstract",
    "Introduction": "introduction",
    "Results": "results",
    "Results and discussion": "results_discussion",
    "Discussion": "discussion",
    "Methods": "methods",
    "Data availability": "data_availability",
    "Code availability": "code_availability",
}


@dataclass
class JournalCandidate:
    doi: str
    title: str = ""
    year: int = 0
    published_date: str = ""
    url: str = ""
    authors: str = ""
    cited_by: int = 0
    crossref_abstract: str = ""
    subjects: str = ""
    query_hits: set[str] = field(default_factory=set)
    preliminary_score: float = 0.0


class JournalStyleAnalyzer:
    def __init__(self, settings: Settings, transport: httpx.BaseTransport | None = None) -> None:
        self.settings = settings
        self._client = httpx.Client(
            timeout=max(settings.request_timeout_sec * 2, 30.0),
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def analyze(
        self,
        *,
        journal: str = "nature-communications",
        query: str | None = None,
        from_year: int = 2020,
        to_year: int | None = None,
        target_size: int = 100,
        target_dir: str | None = None,
        refresh: bool = False,
        skip_pdfs: bool = False,
        pdf_report: bool = False,
        dry_run: bool = False,
    ) -> JournalStyleAnalysisResponse:
        profile = get_journal_profile(journal)
        to_year = to_year or dt.date.today().year
        _validate_year_range(from_year, to_year)
        target_size = _validate_target_size(target_size)
        root = Path(target_dir).expanduser().resolve() if target_dir else _default_target_dir(profile, from_year, to_year)
        planned_paths = _paths(root)
        if dry_run:
            return JournalStyleAnalysisResponse(
                status="ok",
                generated_at=now_utc_iso(),
                journal=profile.label,
                journal_key=profile.key,
                query=query,
                from_year=from_year,
                to_year=to_year,
                target_size=target_size,
                article_count=0,
                target_dir=str(root),
                dry_run=True,
                paths={key: str(value) for key, value in planned_paths.items()},
                metrics={"will_write_files": False},
                next_actions=["Run the same command without dry_run to collect and analyze the journal corpus."],
            )

        _ensure_dirs(root)
        warnings: list[str] = []
        manifest_path = planned_paths["manifest"]
        if manifest_path.exists() and not refresh:
            records = _read_csv(manifest_path)
        else:
            candidates = self._collect_candidates(profile, query=query, from_year=from_year, to_year=to_year)
            _write_csv(planned_paths["candidate_pool"], [_candidate_row(item, profile) for item in candidates.values()])
            records, parse_warnings = self._parse_candidates(
                profile,
                candidates,
                root=root,
                from_year=from_year,
                to_year=to_year,
                target_size=target_size,
                refresh=refresh,
                skip_pdfs=skip_pdfs,
            )
            warnings.extend(parse_warnings)
            _write_csv(manifest_path, records)
            _write_csv(planned_paths["selection_scores"], _selection_rows(records))
            _write_csv(planned_paths["manual_download_checklist"], _manual_download_rows(records))

        analysis_paths, metrics = self._write_analysis(root, records)
        report_path = self._write_report(root, profile, records, metrics, query=query)
        paths = {key: str(value) for key, value in planned_paths.items()}
        paths.update({key: str(value) for key, value in analysis_paths.items()})
        paths["report_markdown"] = str(report_path)

        if pdf_report:
            pdf_path, pdf_warning = self._build_pdf_report(report_path)
            if pdf_path:
                paths["report_pdf"] = str(pdf_path)
            if pdf_warning:
                warnings.append(pdf_warning)

        article_count = len(records)
        status = "ok" if article_count >= target_size else ("partial" if article_count else "error")
        return JournalStyleAnalysisResponse(
            status=status,
            generated_at=now_utc_iso(),
            journal=profile.label,
            journal_key=profile.key,
            query=query,
            from_year=from_year,
            to_year=to_year,
            target_size=target_size,
            article_count=article_count,
            target_dir=str(root),
            dry_run=False,
            paths=paths,
            metrics=metrics,
            warnings=list(dict.fromkeys(warnings)),
            next_actions=[
                "Open report_markdown for the writing guide.",
                "Inspect corpus_manifest.csv before using the corpus for manuscript guidance.",
            ],
        )

    def _collect_candidates(
        self,
        profile: JournalProfile,
        *,
        query: str | None,
        from_year: int,
        to_year: int,
    ) -> dict[str, JournalCandidate]:
        candidates: dict[str, JournalCandidate] = {}
        queries = [query.strip()] if query and query.strip() else []
        queries.extend(profile.query_terms)
        until_date = f"{to_year}-12-31" if to_year < dt.date.today().year else dt.date.today().isoformat()
        common_filter = (
            f"issn:{profile.issn},type:journal-article,"
            f"from-pub-date:{from_year}-01-01,until-pub-date:{until_date}"
        )
        for term in dict.fromkeys(queries):
            params = {
                "filter": common_filter,
                "rows": "120",
                "query.bibliographic": term,
                "sort": "score",
                "order": "desc",
            }
            items = self._crossref_items(params)
            self._ingest_crossref_items(items, candidates, profile, query_label=term, from_year=from_year, to_year=to_year)
            time.sleep(0.05)
        params = {
            "filter": common_filter,
            "rows": "400",
            "sort": "published",
            "order": "desc",
        }
        self._ingest_crossref_items(self._crossref_items(params), candidates, profile, query_label="recent_fill", from_year=from_year, to_year=to_year)
        for item in candidates.values():
            text = " ".join([item.title, item.crossref_abstract, item.subjects, " ".join(sorted(item.query_hits))])
            item.preliminary_score = _term_score(text, profile.domain_terms) + 0.8 * _term_score(text, profile.method_terms)
        return candidates

    def _crossref_items(self, params: dict[str, str]) -> list[dict[str, Any]]:
        response = self._client.get("https://api.crossref.org/works", params=params)
        response.raise_for_status()
        return list(response.json().get("message", {}).get("items", []))

    def _ingest_crossref_items(
        self,
        items: list[dict[str, Any]],
        candidates: dict[str, JournalCandidate],
        profile: JournalProfile,
        *,
        query_label: str,
        from_year: int,
        to_year: int,
    ) -> None:
        for item in items:
            doi = str(item.get("DOI", "")).lower()
            if profile.doi_prefixes and not any(doi.startswith(prefix) for prefix in profile.doi_prefixes):
                continue
            year, published_date = _date_from_crossref(item)
            if year < from_year or year > to_year:
                continue
            title = " ".join(item.get("title") or []).strip()
            abstract = _clean_text(item.get("abstract", "") or "")
            subjects = "; ".join(item.get("subject", []) or [])
            current = candidates.setdefault(
                doi,
                JournalCandidate(
                    doi=doi,
                    title=title,
                    year=year,
                    published_date=published_date,
                    url=item.get("URL", ""),
                    authors=_format_authors(item),
                    cited_by=int(item.get("is-referenced-by-count", 0) or 0),
                    crossref_abstract=abstract,
                    subjects=subjects,
                ),
            )
            current.query_hits.add(query_label)

    def _parse_candidates(
        self,
        profile: JournalProfile,
        candidates: dict[str, JournalCandidate],
        *,
        root: Path,
        from_year: int,
        to_year: int,
        target_size: int,
        refresh: bool,
        skip_pdfs: bool,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        warnings: list[str] = []
        records: list[dict[str, Any]] = []
        ordered = sorted(candidates.values(), key=lambda item: (item.preliminary_score, item.year, item.cited_by), reverse=True)
        for candidate in ordered[: max(target_size * 6, target_size + 50)]:
            try:
                document, html_path = self._fetch_article_html(profile, candidate, root=root, refresh=refresh)
                record = self._parse_article_html(profile, candidate, document, root=root)
                record["html_path"] = str(html_path)
                if record["has_full_body"]:
                    if skip_pdfs:
                        record["pdf_status"] = "skipped"
                        record["pdf_path"] = ""
                    else:
                        pdf_path, pdf_status = self._download_pdf(profile, record, root=root, refresh=refresh)
                        record["pdf_path"] = str(pdf_path) if pdf_path else ""
                        record["pdf_status"] = pdf_status
                    records.append(record)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"{candidate.doi}: {exc}")
            if len(records) >= target_size:
                break
        records.sort(key=lambda row: (float(row["similarity_score"]), int(row["year"])), reverse=True)
        for rank, record in enumerate(records[:target_size], start=1):
            record["corpus_rank"] = rank
        return records[:target_size], warnings

    def _fetch_article_html(
        self,
        profile: JournalProfile,
        candidate: JournalCandidate,
        *,
        root: Path,
        refresh: bool,
    ) -> tuple[str, Path]:
        article_id = _article_id(candidate.doi)
        html_path = root / "html" / f"{article_id}.html"
        if html_path.exists() and not refresh:
            return html_path.read_text(encoding="utf-8", errors="replace"), html_path
        response = self._client.get(profile.article_base_url + candidate.doi.split("/")[-1])
        response.raise_for_status()
        html_path.write_text(response.text, encoding="utf-8")
        return response.text, html_path

    def _parse_article_html(
        self,
        profile: JournalProfile,
        candidate: JournalCandidate,
        document: str,
        *,
        root: Path,
    ) -> dict[str, Any]:
        soup = BeautifulSoup(document, "html.parser")
        title = _meta_content(soup, "citation_title") or candidate.title
        article_id = _article_id(candidate.doi)
        section_counts: defaultdict[str, int] = defaultdict(int)
        paragraph_lengths: list[int] = []
        sentence_lengths: list[int] = []
        text_parts = [title]
        section_titles: list[str] = []
        for section in soup.find_all("section"):
            title_name = _section_title(section)
            if not title_name or title_name in STOP_SECTION_TITLES:
                continue
            text = _remove_display_html(section)
            if not text:
                continue
            key = _canonical_section(title_name)
            section_counts[f"{key}_words"] += _word_count(text)
            section_titles.append(title_name)
            text_parts.extend([title_name, text])
            for paragraph in section.find_all("p"):
                paragraph_text = " ".join(paragraph.get_text(" ", strip=True).split())
                pc = _word_count(paragraph_text)
                if pc >= 8:
                    paragraph_lengths.append(pc)
                    sentence_lengths.extend(_word_count(sentence) for sentence in _split_sentences(paragraph_text))
        if section_counts["abstract_words"] == 0:
            abstract = _meta_content(soup, "description") or _meta_content(soup, "dc.description") or candidate.crossref_abstract
            section_counts["abstract_words"] = _word_count(abstract)
            if abstract:
                text_parts.extend(["Abstract", abstract])
        figures = soup.find_all("figure")
        tables = soup.find_all("table")
        caption_words = [_word_count(" ".join(fig.get_text(" ", strip=True).split())) for fig in figures]
        caption_words = [value for value in caption_words if value]
        references = len(soup.find_all(id=re.compile(r"^ref-CR\d+"))) or len(soup.find_all(attrs={"data-test": "citation-ref"}))
        body_words = sum(
            section_counts[f"{key}_words"]
            for key in ["introduction", "results", "results_discussion", "discussion", "methods", "other"]
        )
        full_text = "\n\n".join(text_parts)
        text_path = root / "text" / f"{article_id}.txt"
        text_path.write_text(full_text, encoding="utf-8")
        scoring_text = " ".join([title, candidate.crossref_abstract, full_text[:12000]])
        domain_score = _term_score(scoring_text, profile.domain_terms)
        method_score = _term_score(scoring_text, profile.method_terms)
        similarity_score = domain_score + 0.8 * method_score + min(len(candidate.query_hits), 6) * 0.5
        has_full_body = body_words > 800 and (
            section_counts["results_words"] > 0
            or section_counts["results_discussion_words"] > 0
            or section_counts["methods_words"] > 0
        )
        return {
            "doi": candidate.doi,
            "article_id": article_id,
            "url": profile.article_base_url + candidate.doi.split("/")[-1],
            "published_date": _meta_content(soup, "prism.publicationDate") or _meta_content(soup, "dc.date") or candidate.published_date,
            "year": candidate.year,
            "article_type": _meta_content(soup, "citation_article_type"),
            "title": title,
            "authors": candidate.authors,
            "cited_by_crossref": candidate.cited_by,
            "query_hits": "; ".join(sorted(candidate.query_hits)),
            "title_words": _word_count(title),
            "abstract_words": section_counts["abstract_words"],
            "introduction_words": section_counts["introduction_words"],
            "results_words": section_counts["results_words"],
            "results_discussion_words": section_counts["results_discussion_words"],
            "discussion_words": section_counts["discussion_words"],
            "methods_words": section_counts["methods_words"],
            "data_availability_words": section_counts["data_availability_words"],
            "code_availability_words": section_counts["code_availability_words"],
            "other_body_words": section_counts["other_words"],
            "body_words_excluding_abstract": body_words,
            "full_text_words_including_abstract": body_words + section_counts["abstract_words"],
            "paragraph_count": len(paragraph_lengths),
            "median_paragraph_words": _median(paragraph_lengths),
            "median_sentence_words": _median(sentence_lengths),
            "figures": len(figures),
            "tables": len(tables),
            "display_items": len(figures) + len(tables),
            "median_caption_words": _median(caption_words),
            "references": references,
            "citation_density_per_1000_words": round(references / body_words * 1000, 3) if body_words else 0,
            "domain_score": domain_score,
            "method_score": method_score,
            "similarity_score": round(similarity_score, 3),
            "selection_reason": _selection_reason(domain_score, method_score),
            "body_section_titles": " | ".join(section_titles),
            "has_full_body": has_full_body,
            "pdf_url": _meta_content(soup, "citation_pdf_url"),
            "text_path": str(text_path),
        }

    def _download_pdf(
        self,
        profile: JournalProfile,
        record: dict[str, Any],
        *,
        root: Path,
        refresh: bool,
    ) -> tuple[Path | None, str]:
        pdf_path = root / "pdfs" / f"{record['article_id']}.pdf"
        if pdf_path.exists() and pdf_path.stat().st_size > 1000 and not refresh:
            return pdf_path, "existing"
        base = profile.article_base_url + str(record["doi"]).split("/")[-1]
        candidates = [str(record.get("pdf_url") or ""), base + ".pdf", base + "_reference.pdf"]
        for url in [value for value in dict.fromkeys(candidates) if value]:
            try:
                response = self._client.get(url)
                if response.status_code >= 400:
                    continue
                content = response.content
                if content.startswith(b"%PDF") or "pdf" in response.headers.get("content-type", "").lower():
                    pdf_path.write_bytes(content)
                    return pdf_path, "downloaded"
            except httpx.HTTPError:
                continue
        return None, "failed"

    def _write_analysis(self, root: Path, records: list[dict[str, Any]]) -> tuple[dict[str, Path], dict[str, Any]]:
        section_rows = []
        sentence_rows = []
        caption_rows = []
        reference_rows = []
        claim_counter: Counter[str] = Counter()
        hedge_counter: Counter[str] = Counter()
        phrase_counter: Counter[str] = Counter()
        for row in records:
            for section in ["abstract", "introduction", "results", "results_discussion", "discussion", "methods", "data_availability", "code_availability"]:
                section_rows.append({"doi": row["doi"], "year": row["year"], "section": section, "words": row.get(f"{section}_words", 0)})
            text_path = Path(str(row.get("text_path") or ""))
            text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""
            for sentence in _split_sentences(text)[:600]:
                wc = _word_count(sentence)
                sentence_rows.append({"doi": row["doi"], "year": row["year"], "sentence_words": wc})
                low = _normalized(sentence)
                for verb in CLAIM_VERBS:
                    if re.search(rf"\b{re.escape(verb)}(?:s|ed|ing)?\b", low):
                        claim_counter[verb] += 1
                for hedge in HEDGE_WORDS:
                    if re.search(rf"\b{re.escape(hedge)}\b", low):
                        hedge_counter[hedge] += 1
                tokens = [word.lower() for word in _words(sentence) if len(word) > 3]
                for n in (2, 3):
                    for idx in range(len(tokens) - n + 1):
                        phrase_counter[" ".join(tokens[idx : idx + n])] += 1
            caption_rows.append(
                {
                    "doi": row["doi"],
                    "year": row["year"],
                    "figures": row.get("figures", 0),
                    "tables": row.get("tables", 0),
                    "display_items": row.get("display_items", 0),
                    "median_caption_words": row.get("median_caption_words", 0),
                }
            )
            reference_rows.append(
                {
                    "doi": row["doi"],
                    "year": row["year"],
                    "references": row.get("references", 0),
                    "body_words_excluding_abstract": row.get("body_words_excluding_abstract", 0),
                    "citation_density_per_1000_words": row.get("citation_density_per_1000_words", 0),
                }
            )
        paths = {
            "section_stats": root / "analysis" / "section_stats.csv",
            "sentence_stats": root / "analysis" / "sentence_stats.csv",
            "caption_stats": root / "analysis" / "caption_stats.csv",
            "reference_stats": root / "analysis" / "reference_stats.csv",
            "phrase_bank": root / "analysis" / "phrase_bank.csv",
            "citation_matrix": root / "data" / "citation_matrix.csv",
        }
        _write_csv(paths["section_stats"], section_rows)
        _write_csv(paths["sentence_stats"], sentence_rows)
        _write_csv(paths["caption_stats"], caption_rows)
        _write_csv(paths["reference_stats"], reference_rows)
        _write_csv(paths["citation_matrix"], reference_rows)
        phrase_rows = (
            [{"category": "claim_verb", "item": key, "count": value} for key, value in claim_counter.most_common()]
            + [{"category": "hedge_word", "item": key, "count": value} for key, value in hedge_counter.most_common()]
            + [{"category": "frequent_phrase", "item": key, "count": value} for key, value in phrase_counter.most_common(120)]
        )
        _write_csv(paths["phrase_bank"], phrase_rows)
        metrics = _summary_metrics(records)
        metrics["top_claim_verbs"] = dict(claim_counter.most_common(10))
        metrics["top_hedge_words"] = dict(hedge_counter.most_common(10))
        return paths, metrics

    def _write_report(
        self,
        root: Path,
        profile: JournalProfile,
        records: list[dict[str, Any]],
        metrics: dict[str, Any],
        *,
        query: str | None,
    ) -> Path:
        year_counts = Counter(int(row["year"]) for row in records)
        reason_counts = Counter(str(row.get("selection_reason") or "") for row in records)
        lines = [
            f"# {profile.label} journal style analysis",
            "",
            f"Generated at: `{now_utc_iso()}`",
            "",
            "## Corpus",
            "",
            f"- Query focus: {query or 'profile default terms'}",
            f"- Article count: {len(records)}",
            f"- Year distribution: {_format_counter(year_counts)}",
            f"- Selection reasons: {_format_counter(reason_counts)}",
            "",
            "## Length and structure",
            "",
            "| Metric | Median (IQR) |",
            "| --- | ---: |",
            f"| Title words | {_median_iqr(records, 'title_words')} |",
            f"| Abstract words | {_median_iqr(records, 'abstract_words')} |",
            f"| Body words excluding abstract | {_median_iqr(records, 'body_words_excluding_abstract')} |",
            f"| Methods words | {_median_iqr(records, 'methods_words')} |",
            f"| Display items | {_median_iqr(records, 'display_items')} |",
            f"| Median caption words | {_median_iqr(records, 'median_caption_words')} |",
            f"| References | {_median_iqr(records, 'references')} |",
            "",
            "## Writing guidance",
            "",
            "- Use result-led section headings rather than process-led headings.",
            "- Put corpus selection, scoring rules, and parser limits in Methods or supplementary material.",
            "- Use the report metrics as soft style priors, not as hard journal requirements.",
            "- Keep the generated phrase bank as a guide to recurring rhetorical moves rather than copied text.",
            "",
            "## Top selected articles",
            "",
        ]
        for row in sorted(records, key=lambda item: float(item.get("similarity_score") or 0), reverse=True)[:20]:
            lines.append(
                f"{int(row['corpus_rank'])}. {int(row['year'])}; score {float(row['similarity_score']):.1f}; "
                f"{row.get('selection_reason')}: {row.get('title')}"
            )
            lines.append("")
        lines.extend(
            [
                "## Reproducibility",
                "",
                "- Metadata source: Crossref.",
                "- Article text source: journal article HTML with optional PDF download.",
                "- Report boundary: structural and stylistic statistics only; no long verbatim article reproduction.",
                "",
            ]
        )
        report_path = root / "report" / "journal_style_report.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")
        (root / "analysis" / "summary_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
        return report_path

    def _build_pdf_report(self, report_path: Path) -> tuple[Path | None, str | None]:
        if not shutil.which("pandoc") or not shutil.which("xelatex"):
            return None, "PDF report skipped because pandoc or xelatex is not available."
        pdf_path = report_path.with_suffix(".pdf")
        result = subprocess.run(
            [
                "pandoc",
                str(report_path.name),
                "-o",
                str(pdf_path.name),
                "--pdf-engine=xelatex",
                "-V",
                "papersize=a4",
                "-V",
                "fontsize=10pt",
                "-V",
                "geometry:margin=2.2cm",
                "-V",
                "linestretch=1.08",
                "-V",
                "urlstyle=same",
                "-V",
                "header-includes=\\sloppy",
                "-V",
                "header-includes=\\emergencystretch=3em",
                "-V",
                "mainfont=Noto Serif CJK SC",
                "-V",
                "CJKmainfont=Noto Serif CJK SC",
            ],
            cwd=report_path.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        (report_path.parent / "pandoc_build.log").write_text(result.stdout, encoding="utf-8")
        if result.returncode != 0 or not pdf_path.exists():
            return None, "PDF report failed; inspect pandoc_build.log."
        return pdf_path, None


def _default_target_dir(profile: JournalProfile, from_year: int, to_year: int) -> Path:
    return APP_HOME / "journal_style" / f"{profile.key}_{from_year}_{to_year}"


def _paths(root: Path) -> dict[str, Path]:
    return {
        "manifest": root / "data" / "corpus_manifest.csv",
        "candidate_pool": root / "data" / "candidate_pool_raw.csv",
        "selection_scores": root / "data" / "selection_scores.csv",
        "manual_download_checklist": root / "data" / "manual_download_checklist.csv",
    }


def _ensure_dirs(root: Path) -> None:
    for name in ["data", "analysis", "html", "text", "pdfs", "report"]:
        (root / name).mkdir(parents=True, exist_ok=True)


def _validate_year_range(from_year: int, to_year: int) -> None:
    current_year = dt.date.today().year
    if from_year < 1900 or to_year > current_year + 1 or from_year > to_year:
        raise ValueError("invalid year range")


def _validate_target_size(value: int) -> int:
    if value < 1 or value > 500:
        raise ValueError("target_size must be between 1 and 500")
    return value


def _clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return " ".join(value.split())


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9'’-]*", text)


def _word_count(text: str) -> int:
    return len(_words(text))


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text) if _word_count(part) >= 3]


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _term_score(text: str, terms: dict[str, float]) -> float:
    low = _normalized(text)
    return round(sum(weight for term, weight in terms.items() if term in low), 3)


def _date_from_crossref(item: dict[str, Any]) -> tuple[int, str]:
    for field_name in ["published-online", "published-print", "published", "issued"]:
        parts = (item.get(field_name) or {}).get("date-parts", [[]])[0]
        if parts:
            year = int(parts[0])
            date = "-".join(str(part).zfill(2) if idx else str(part) for idx, part in enumerate(parts))
            return year, date
    return 0, ""


def _format_authors(item: dict[str, Any], limit: int = 8) -> str:
    authors = []
    for author in item.get("author", [])[:limit]:
        full = " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part)
        if full:
            authors.append(full)
    if len(item.get("author", [])) > limit:
        authors.append("et al.")
    return "; ".join(authors)


def _article_id(doi: str) -> str:
    return doi.split("/")[-1].replace(".", "_")


def _meta_content(soup: BeautifulSoup, name: str) -> str:
    tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
    return html.unescape(tag.get("content", "")).strip() if tag else ""


def _section_title(section) -> str:
    title = section.get("data-title", "") or ""
    if not title:
        heading = section.find(["h2", "h3"])
        if heading:
            title = heading.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", title).strip()


def _remove_display_html(node) -> str:
    soup = BeautifulSoup(str(node), "html.parser")
    for tag in soup.find_all(["figure", "table", "script", "style"]):
        tag.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def _canonical_section(title: str) -> str:
    if title in CANONICAL_SECTIONS:
        return CANONICAL_SECTIONS[title]
    low = title.strip().lower()
    for canonical, key in CANONICAL_SECTIONS.items():
        if low == canonical.lower():
            return key
    return "other"


def _median(values: list[int]) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    mid = len(values) // 2
    if len(values) % 2:
        return float(values[mid])
    return float((values[mid - 1] + values[mid]) / 2)


def _selection_reason(domain_score: float, method_score: float) -> str:
    if domain_score >= 8 and method_score >= 5:
        return "domain+method comparator"
    if domain_score >= 8:
        return "domain comparator"
    if method_score >= 6:
        return "method comparator"
    return "journal style comparator"


def _candidate_row(item: JournalCandidate, profile: JournalProfile) -> dict[str, Any]:
    text = " ".join([item.title, item.crossref_abstract, item.subjects, " ".join(sorted(item.query_hits))])
    return {
        "doi": item.doi,
        "year": item.year,
        "title": item.title,
        "published_date": item.published_date,
        "query_hits": "; ".join(sorted(item.query_hits)),
        "preliminary_score": item.preliminary_score,
        "domain_score": _term_score(text, profile.domain_terms),
        "method_score": _term_score(text, profile.method_terms),
        "url": profile.article_base_url + item.doi.split("/")[-1],
    }


def _selection_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "corpus_rank": row.get("corpus_rank"),
            "doi": row.get("doi"),
            "year": row.get("year"),
            "title": row.get("title"),
            "domain_score": row.get("domain_score"),
            "method_score": row.get("method_score"),
            "similarity_score": row.get("similarity_score"),
            "selection_reason": row.get("selection_reason"),
            "query_hits": row.get("query_hits"),
            "url": row.get("url"),
        }
        for row in records
    ]


def _manual_download_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "doi": row.get("doi"),
            "title": row.get("title"),
            "url": row.get("url"),
            "pdf_status": row.get("pdf_status"),
            "note": "PDF unavailable from automatic URL probing.",
        }
        for row in records
        if row.get("pdf_status") == "failed"
    ]


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row}) if rows else ["status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _format_counter(counter: Counter[Any]) -> str:
    if not counter:
        return "none"
    return "; ".join(f"{key}: {value}" for key, value in sorted(counter.items(), key=lambda item: str(item[0])))


def _summary_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "article_count": len(records),
        "year_counts": dict(Counter(str(row.get("year")) for row in records)),
        "pdf_downloaded_count": sum(1 for row in records if row.get("pdf_status") in {"downloaded", "existing"}),
        "full_body_count": sum(1 for row in records if str(row.get("has_full_body")).lower() in {"true", "1"}),
        "median_body_words": _median([int(float(row.get("body_words_excluding_abstract") or 0)) for row in records]),
        "median_abstract_words": _median([int(float(row.get("abstract_words") or 0)) for row in records]),
        "median_references": _median([int(float(row.get("references") or 0)) for row in records]),
    }


def _median_iqr(records: list[dict[str, Any]], key: str) -> str:
    values = sorted(float(row.get(key) or 0) for row in records)
    if not values:
        return "NA"
    return f"{_quantile(values, 0.5):.0f} ({_quantile(values, 0.25):.0f}-{_quantile(values, 0.75):.0f})"


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    idx = (len(values) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(values) - 1)
    frac = idx - lo
    return values[lo] * (1 - frac) + values[hi] * frac
