from __future__ import annotations

import math
from datetime import UTC, datetime

from research_mcp.models import LiteratureResult
from research_mcp.utils import canonical_doi, completeness_score, normalize_title, tokenize, year_from_any


SOURCE_WEIGHTS = {
    "OpenAlex": 3.0,
    "PubMed": 3.0,
    "Europe PMC": 2.8,
    "Semantic Scholar": 2.5,
    "arXiv": 2.2,
    "Crossref": 1.8,
    "DOAJ": 1.4,
    "CORE": 1.2,
}


def dedupe_and_rank(
    results: list[LiteratureResult],
    *,
    query: str,
    sort: str,
    limit: int,
) -> list[LiteratureResult]:
    merged: dict[str, LiteratureResult] = {}
    for result in results:
        key = _identity_key(result)
        current = merged.get(key)
        if current is None:
            merged[key] = result
            continue
        merged[key] = _merge_results(current, result)

    ranked: list[LiteratureResult] = []
    for result in merged.values():
        result.score = round(_score_result(result, query=query, sort=sort), 4)
        ranked.append(result)

    if sort == "recent":
        ranked.sort(key=lambda item: (_recency_key(item), item.score or 0.0, item.title or ""), reverse=True)
    else:
        ranked.sort(key=lambda item: (item.score or 0.0, _recency_key(item), item.title or ""), reverse=True)
    return ranked[:limit]


def _identity_key(result: LiteratureResult) -> str:
    doi = canonical_doi(result.doi)
    if doi:
        return f"doi:{doi}"
    if result.pmid:
        return f"pmid:{result.pmid}"
    if result.landing_url:
        return f"url:{result.landing_url.strip().lower()}"
    title = normalize_title(result.title)
    if title:
        return f"title:{title}"
    return f"source:{result.source}:{result.source_id or result.title or 'unknown'}"


def _merge_results(left: LiteratureResult, right: LiteratureResult) -> LiteratureResult:
    primary = left if completeness_score(left) >= completeness_score(right) else right
    secondary = right if primary is left else left
    merged = primary.model_copy(deep=True)
    for field in [
        "title",
        "abstract",
        "year",
        "published_date",
        "doi",
        "pmid",
        "landing_url",
        "pdf_url",
        "journal",
        "publisher",
        "open_access_url",
        "license",
    ]:
        if getattr(merged, field) is None and getattr(secondary, field) is not None:
            setattr(merged, field, getattr(secondary, field))

    merged.authors = merged.authors or secondary.authors
    merged.citation_count = max(value for value in [merged.citation_count, secondary.citation_count] if value is not None) if any(
        value is not None for value in [merged.citation_count, secondary.citation_count]
    ) else None
    if merged.is_open_access is None:
        merged.is_open_access = secondary.is_open_access
    merged.extras = {**secondary.extras, **merged.extras}
    merged_sources = sorted(set(merged.extras.get("merged_sources", [])) | {left.source, right.source})
    merged.extras["merged_sources"] = merged_sources
    return merged


def _score_result(result: LiteratureResult, *, query: str, sort: str) -> float:
    title = (result.title or "").lower()
    abstract = (result.abstract or "").lower()
    tokens = tokenize(query)
    if not tokens:
        return 0.0

    title_overlap = sum(1 for token in tokens if token in title)
    abstract_overlap = sum(1 for token in tokens if token in abstract)
    overlap_ratio = title_overlap / len(tokens)
    score = overlap_ratio * 35.0

    if query.lower() in title:
        score += 25.0
    score += (abstract_overlap / len(tokens)) * 8.0
    score += SOURCE_WEIGHTS.get(result.source, 1.0)

    if result.citation_count:
        citation_weight = 3.0 if sort == "relevance" else 1.25
        score += min(math.log1p(result.citation_count) * citation_weight, 18.0)

    if result.is_open_access:
        score += 4.0
    if result.doi:
        score += 1.0
    if result.pdf_url:
        score += 1.0
    if result.abstract:
        score += 1.0

    recency_bonus = _recency_key(result)
    score += recency_bonus * (1.6 if sort == "recent" else 0.45)
    return score


def _recency_key(result: LiteratureResult) -> float:
    current_year = datetime.now(tz=UTC).year
    year = result.year or year_from_any(result.published_date)
    if not year:
        return 0.0
    return max(0.0, float(6 - min(current_year - year, 6)))
