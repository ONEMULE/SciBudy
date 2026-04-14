from __future__ import annotations

from research_mcp.models import LiteratureResult
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import canonical_doi, extract_authors_from_names, safe_int, year_from_any


class PubMedProvider(BaseProvider):
    name = "PubMed"
    cache_ttl_sec = 6 * 60 * 60
    min_interval_sec = 0.34
    enabled_flag = "enable_pubmed"

    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit}
        params["sort"] = "pub_date" if sort == "recent" else "relevance"
        if self.settings.ncbi_api_key:
            params["api_key"] = self.settings.ncbi_api_key
        esearch, _ = self.client.get_json(
            provider_name=self.name,
            url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params=params,
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        ids = esearch.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        summary_params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        if self.settings.ncbi_api_key:
            summary_params["api_key"] = self.settings.ncbi_api_key
        summary, _ = self.client.get_json(
            provider_name=self.name,
            url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params=summary_params,
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        result_block = summary.get("result", {})
        results: list[LiteratureResult] = []
        for pmid in ids:
            item = result_block.get(pmid, {})
            doi = None
            for article_id in item.get("articleids", []):
                if article_id.get("idtype") == "doi":
                    doi = article_id.get("value")
                    break
            published_date = item.get("sortpubdate") or item.get("pubdate")
            results.append(
                LiteratureResult(
                    title=item.get("title"),
                    authors=extract_authors_from_names(item.get("authors", [])),
                    year=safe_int(item.get("pubdate", "")[:4]) or year_from_any(published_date),
                    published_date=published_date,
                    doi=canonical_doi(doi),
                    pmid=pmid,
                    source=self.name,
                    source_id=pmid,
                    landing_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    journal=item.get("fulljournalname") or item.get("source"),
                    extras={"pubtype": item.get("pubtype")},
                )
            )
        return results
