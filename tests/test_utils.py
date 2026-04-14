from research_mcp.utils import canonical_doi, openalex_abstract, parse_date_parts


def test_openalex_abstract_reconstruction():
    text = openalex_abstract({"hello": [1], "world": [0]})
    assert text == "world hello"


def test_parse_date_parts_and_canonical_doi():
    assert parse_date_parts([[2024, 12, 5]]) == "2024-12-05"
    assert canonical_doi("https://doi.org/10.1000/ABC") == "10.1000/abc"
