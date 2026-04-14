from __future__ import annotations

from research_mcp.models import LiteratureResult
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import canonical_doi, extract_authors_from_names, normalize_whitespace, pick_url, year_from_any


class DOAJProvider(BaseProvider):
    name = "DOAJ"
    cache_ttl_sec = 12 * 60 * 60
    min_interval_sec = 0.5
    enabled_flag = "enable_doaj"

    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        data, _ = self.client.get_json(
            provider_name=self.name,
            url=f"https://doaj.org/api/search/articles/{query}",
            params={"pageSize": limit},
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        items = data.get("results") or data.get("hits", {}).get("hits", [])
        results: list[LiteratureResult] = []
        for item in items:
            payload = item.get("bibjson") or item.get("_source", {}).get("bibjson") or {}
            identifiers = payload.get("identifier") or []
            doi = None
            for identifier in identifiers:
                if str(identifier.get("type", "")).lower() == "doi":
                    doi = identifier.get("id")
                    break
            links = payload.get("link") or []
            licenses = payload.get("license") or []
            published_date = normalize_whitespace(payload.get("year"))
            results.append(
                LiteratureResult(
                    title=normalize_whitespace(payload.get("title")),
                    abstract=normalize_whitespace(payload.get("abstract")),
                    authors=extract_authors_from_names(payload.get("author", [])),
                    year=year_from_any(published_date),
                    published_date=published_date,
                    doi=canonical_doi(doi),
                    source=self.name,
                    source_id=item.get("id") or item.get("_id"),
                    landing_url=pick_url(links),
                    pdf_url=pick_url([link for link in links if str(link.get("type", "")).lower() == "fulltext"]),
                    journal=normalize_whitespace((payload.get("journal") or {}).get("title")),
                    is_open_access=True,
                    open_access_url=pick_url(links),
                    license=pick_url(licenses),
                    extras={},
                )
            )
        return results
