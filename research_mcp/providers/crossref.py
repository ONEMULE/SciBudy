from __future__ import annotations

from research_mcp.models import LiteratureResult
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import canonical_doi, extract_authors_from_names, normalize_whitespace, parse_date_parts, pick_url


class CrossrefProvider(BaseProvider):
    name = "Crossref"
    cache_ttl_sec = 24 * 60 * 60
    min_interval_sec = 1.0
    enabled_flag = "enable_crossref"

    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        params = {"query": query, "rows": limit}
        if sort == "recent":
            params["sort"] = "published"
            params["order"] = "desc"
        if self.settings.crossref_mailto:
            params["mailto"] = self.settings.crossref_mailto
        data, _ = self.client.get_json(
            provider_name=self.name,
            url="https://api.crossref.org/works",
            params=params,
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        results: list[LiteratureResult] = []
        for item in data.get("message", {}).get("items", []):
            title = item.get("title") or []
            published_date = parse_date_parts(
                (item.get("published-print") or item.get("published-online") or item.get("issued") or item.get("created") or {}).get(
                    "date-parts"
                )
            )
            license_items = item.get("license") or []
            results.append(
                LiteratureResult(
                    title=normalize_whitespace(title[0] if title else None),
                    abstract=normalize_whitespace(item.get("abstract")),
                    authors=extract_authors_from_names(item.get("author", [])),
                    year=int(published_date[:4]) if published_date else None,
                    published_date=published_date,
                    doi=canonical_doi(item.get("DOI")),
                    source=self.name,
                    source_id=item.get("DOI"),
                    landing_url=pick_url(item.get("URL")),
                    journal=normalize_whitespace((item.get("container-title") or [None])[0]),
                    publisher=normalize_whitespace(item.get("publisher")),
                    is_open_access=bool(license_items) if license_items else None,
                    license=pick_url(license_items),
                    extras={"type": item.get("type")},
                )
            )
        return results
