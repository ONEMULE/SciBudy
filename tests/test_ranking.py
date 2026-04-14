from research_mcp.models import LiteratureResult
from research_mcp.ranking import dedupe_and_rank


def test_dedupe_merges_duplicate_doi_and_keeps_richer_fields():
    left = LiteratureResult(
        title="A test paper",
        abstract="Detailed abstract",
        authors=["Alice"],
        year=2025,
        doi="10.1000/example",
        source="OpenAlex",
        source_id="OA1",
        landing_url="https://openalex.org/W1",
    )
    right = LiteratureResult(
        title="A test paper",
        authors=["Alice", "Bob"],
        year=2025,
        doi="https://doi.org/10.1000/example",
        source="Crossref",
        source_id="CR1",
        landing_url="https://doi.org/10.1000/example",
        citation_count=120,
    )

    ranked = dedupe_and_rank([left, right], query="test paper", sort="relevance", limit=10)

    assert len(ranked) == 1
    assert ranked[0].citation_count == 120
    assert ranked[0].abstract == "Detailed abstract"
    assert ranked[0].extras["merged_sources"] == ["Crossref", "OpenAlex"]
