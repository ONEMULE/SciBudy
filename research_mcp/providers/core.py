from __future__ import annotations

from research_mcp.models import LiteratureResult
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import canonical_doi, extract_authors_from_names, first_non_empty, normalize_whitespace, pick_url, safe_int


class COREProvider(BaseProvider):
    name = "CORE"
    cache_ttl_sec = 12 * 60 * 60
    min_interval_sec = 1.0
    enabled_flag = "enable_core"
    required_settings = (("CORE_API_KEY", "core_api_key"),)

    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        data, _ = self.client.get_json(
            provider_name=self.name,
            url="https://api.core.ac.uk/v3/search/works",
            params={"q": query, "limit": limit},
            headers={"Authorization": f"Bearer {self.settings.core_api_key}"},
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        results: list[LiteratureResult] = []
        for item in data.get("results", []):
            results.append(
                LiteratureResult(
                    title=normalize_whitespace(item.get("title")),
                    abstract=normalize_whitespace(item.get("abstract")),
                    authors=extract_authors_from_names(item.get("authors", [])),
                    year=safe_int(item.get("yearPublished")),
                    published_date=first_non_empty(item.get("publishedDate"), item.get("yearPublished")),
                    doi=canonical_doi(item.get("doi")),
                    source=self.name,
                    source_id=str(item.get("id")) if item.get("id") is not None else None,
                    landing_url=pick_url(first_non_empty(item.get("sourceFulltextUrls"), item.get("downloadUrl"), item.get("urls"))),
                    pdf_url=pick_url(first_non_empty(item.get("downloadUrl"), item.get("sourceFulltextUrls"))),
                    journal=normalize_whitespace((item.get("journals") or [{}])[0].get("title") if item.get("journals") else None),
                    is_open_access=bool(item.get("downloadUrl") or item.get("sourceFulltextUrls")),
                    open_access_url=pick_url(first_non_empty(item.get("downloadUrl"), item.get("sourceFulltextUrls"))),
                    extras={},
                )
            )
        return results
