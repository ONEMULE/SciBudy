import json

import httpx

from research_mcp.cli import build_parser, dispatch
from research_mcp.journal_style import JournalStyleAnalyzer
from research_mcp.journal_style import JournalTextStandardizer
from research_mcp.settings import Settings


LONG_RESULTS = " ".join(
    [
        "We show that posterior inference improves model diagnostics and constrains NOx ozone chemistry with aircraft observations."
        for _ in range(90)
    ]
)
LONG_METHODS = " ".join(
    [
        "We used a simulation ensemble and calibration diagnostics to evaluate uncertainty in atmospheric chemistry models."
        for _ in range(55)
    ]
)

ARTICLE_HTML = f"""
<html><head>
<meta name="citation_title" content="Observation constrained atmospheric inference">
<meta name="citation_pdf_url" content="https://www.nature.com/articles/s41467-025-00001-1.pdf">
<meta name="prism.publicationDate" content="2025-01-02">
</head><body>
<section data-title="Abstract"><p>Bayesian inference constrains atmospheric chemistry with observations.</p></section>
<section data-title="Introduction"><p>Atmospheric chemistry and air quality models require observational constraints.</p></section>
<section data-title="Results"><p>{LONG_RESULTS}</p></section>
<section data-title="Methods"><p>{LONG_METHODS}</p></section>
<section data-title="Data availability"><p>Data are available.</p></section>
<figure><figcaption>Fig. 1 Posterior diagnostics for atmospheric chemistry.</figcaption></figure>
<ol><li id="ref-CR1">Reference 1</li><li id="ref-CR2">Reference 2</li></ol>
</body></html>
"""


def make_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "api.crossref.org/works" in url:
            payload = {
                "message": {
                    "items": [
                        {
                            "DOI": "10.1038/s41467-025-00001-1",
                            "title": ["Observation constrained atmospheric inference"],
                            "published-online": {"date-parts": [[2025, 1, 2]]},
                            "author": [{"given": "A.", "family": "Author"}],
                            "subject": ["Atmospheric Science"],
                            "abstract": "<p>Bayesian inference for atmospheric chemistry.</p>",
                            "is-referenced-by-count": 10,
                            "URL": "https://doi.org/10.1038/s41467-025-00001-1",
                        }
                    ]
                }
            }
            return httpx.Response(200, json=payload)
        if url.endswith(".pdf"):
            return httpx.Response(200, content=b"%PDF-1.4\n%fixture\n", headers={"content-type": "application/pdf"})
        if "nature.com/articles/s41467-025-00001-1" in url:
            return httpx.Response(200, text=ARTICLE_HTML)
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def test_journal_style_dry_run_has_no_side_effects(tmp_path):
    analyzer = JournalStyleAnalyzer(
        Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        transport=make_transport(),
    )

    response = analyzer.analyze(target_dir=str(tmp_path / "corpus"), target_size=1, dry_run=True)

    assert response.status == "ok"
    assert response.dry_run is True
    assert response.article_count == 0
    assert response.metrics["will_write_files"] is False
    assert not (tmp_path / "corpus").exists()


def test_journal_style_collects_and_writes_reports(tmp_path):
    analyzer = JournalStyleAnalyzer(
        Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        transport=make_transport(),
    )

    response = analyzer.analyze(
        journal="nature-communications",
        query="atmospheric inference",
        from_year=2025,
        to_year=2025,
        target_size=1,
        target_dir=str(tmp_path / "corpus"),
    )

    assert response.status == "ok"
    assert response.article_count == 1
    assert response.metrics["full_body_count"] == 1
    assert response.metrics["pdf_downloaded_count"] == 1
    assert "manifest" in response.paths
    assert "report_markdown" in response.paths
    assert (tmp_path / "corpus" / "data" / "corpus_manifest.csv").exists()
    assert (tmp_path / "corpus" / "analysis" / "phrase_bank.csv").exists()
    assert (tmp_path / "corpus" / "report" / "journal_style_report.md").exists()


def test_journal_style_cached_manifest_reanalysis(tmp_path):
    analyzer = JournalStyleAnalyzer(
        Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        transport=make_transport(),
    )
    first = analyzer.analyze(from_year=2025, to_year=2025, target_size=1, target_dir=str(tmp_path / "corpus"))
    second = analyzer.analyze(from_year=2025, to_year=2025, target_size=1, target_dir=str(tmp_path / "corpus"))

    assert first.article_count == 1
    assert second.article_count == 1
    metrics = json.loads((tmp_path / "corpus" / "analysis" / "summary_metrics.json").read_text())
    assert metrics["article_count"] == 1


def make_standardization_corpus(tmp_path):
    corpus = tmp_path / "journal-corpus"
    (corpus / "text").mkdir(parents=True)
    (corpus / "text" / "article-1.txt").write_text(
        "Atmospheric observations show model bias. The analysis uses simulations and evidence from measurements.",
        encoding="utf-8",
    )
    (corpus / "text" / "article-2.txt").write_text(
        "These results indicate that posterior estimates constrain chemistry and reduce uncertainty.",
        encoding="utf-8",
    )
    return corpus


def test_journal_standardizer_dry_run_has_no_side_effects(tmp_path):
    corpus = make_standardization_corpus(tmp_path)
    manuscript = tmp_path / "draft.tex"
    manuscript.write_text(
        "\\title{A title with inventedword}\n"
        "The analysis uses simulations and customword.",
        encoding="utf-8",
    )

    response = JournalTextStandardizer().standardize(
        corpus_dir=str(corpus),
        input_path=str(manuscript),
        dry_run=True,
    )

    assert response.dry_run is True
    assert response.oov_unique_count == 1
    assert not (corpus / "standardization").exists()


def test_journal_standardizer_writes_audit_and_allowed_terms(tmp_path):
    corpus = make_standardization_corpus(tmp_path)
    manuscript = tmp_path / "draft.tex"
    manuscript.write_text("The analysis uses DSMACC and customword.", encoding="utf-8")

    response = JournalTextStandardizer().standardize(
        corpus_dir=str(corpus),
        input_path=str(manuscript),
        allowed_terms=["customword"],
    )

    assert response.status == "ok"
    assert response.oov_unique_count == 0
    assert (corpus / "standardization" / "draft" / "journal_vocabulary.csv").exists()
    assert (corpus / "standardization" / "draft" / "oov_report.csv").read_text(encoding="utf-8").strip() == "status"


def test_journal_standardizer_applies_replacement_map_to_copy(tmp_path):
    corpus = make_standardization_corpus(tmp_path)
    manuscript = tmp_path / "draft.txt"
    manuscript.write_text("customword", encoding="utf-8")
    replacements = tmp_path / "replacements.csv"
    replacements.write_text("word,replacement\ncustomword,analysis\n", encoding="utf-8")

    response = JournalTextStandardizer().standardize(
        corpus_dir=str(corpus),
        input_path=str(manuscript),
        replacement_map=str(replacements),
        apply=True,
        latex_mode=False,
    )

    standardized = corpus / "standardization" / "draft" / "standardized.txt"
    assert response.applied is True
    assert standardized.exists()
    assert "analysis" in standardized.read_text(encoding="utf-8")
    assert "customword" in manuscript.read_text(encoding="utf-8")


def test_journal_standardize_cli_json(tmp_path, capsys):
    corpus = make_standardization_corpus(tmp_path)
    manuscript = tmp_path / "draft.txt"
    manuscript.write_text("The analysis uses simulations.", encoding="utf-8")

    args = build_parser().parse_args(
        [
            "journal-standardize",
            "--corpus-dir",
            str(corpus),
            "--input",
            str(manuscript),
            "--plain-text",
            "--format",
            "json",
        ]
    )
    dispatch(args)

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["oov_unique_count"] == 0
