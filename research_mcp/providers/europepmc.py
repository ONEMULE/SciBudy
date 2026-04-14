from __future__ import annotations

from research_mcp.models import LiteratureResult
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import canonical_doi, normalize_whitespace, pick_url, safe_int


class EuropePMCProvider(BaseProvider):
    name = "Europe PMC"
    cache_ttl_sec = 6 * 60 * 60
    min_interval_sec = 0.5
    enabled_flag = "enable_europepmc"

    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        data, _ = self.client.get_json(
            provider_name=self.name,
            url="https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": query, "format": "json", "pageSize": limit},
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        results: list[LiteratureResult] = []
        for item in data.get("resultList", {}).get("result", []):
            pmid = item.get("pmid")
            landing_url = (
                pick_url(item.get("fullTextUrlList", {}).get("fullTextUrl"))
                or (f"https://europepmc.org/article/MED/{pmid}" if pmid else None)
                or item.get("journalUrl")
            )
            results.append(
                LiteratureResult(
                    title=normalize_whitespace(item.get("title")),
                    authors=[name.strip() for name in (item.get("authorString") or "").split(",") if name.strip()],
                    year=safe_int(item.get("pubYear")),
                    published_date=str(item.get("firstPublicationDate") or item.get("pubYear") or ""),
                    doi=canonical_doi(item.get("doi")),
                    pmid=pmid,
                    source=self.name,
                    source_id=item.get("id") or pmid,
                    landing_url=landing_url,
                    journal=normalize_whitespace(item.get("journalTitle")),
                    is_open_access=str(item.get("isOpenAccess")).lower() == "y" if item.get("isOpenAccess") is not None else None,
                    open_access_url=landing_url,
                    extras={"source": item.get("source")},
                )
            )
        return results
