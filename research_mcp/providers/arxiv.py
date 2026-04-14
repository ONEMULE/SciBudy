from __future__ import annotations

import xml.etree.ElementTree as ET

from research_mcp.models import LiteratureResult
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import normalize_whitespace, year_from_any


ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}


class ArxivProvider(BaseProvider):
    name = "arXiv"
    cache_ttl_sec = 12 * 60 * 60
    min_interval_sec = 3.0
    enabled_flag = "enable_arxiv"

    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        sort_by = "submittedDate" if sort == "recent" else "relevance"
        xml_text, _ = self.client.get_text(
            provider_name=self.name,
            url="https://export.arxiv.org/api/query",
            params={
                "search_query": query,
                "start": 0,
                "max_results": limit,
                "sortBy": sort_by,
                "sortOrder": "descending",
            },
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        root = ET.fromstring(xml_text)
        results: list[LiteratureResult] = []
        for entry in root.findall("a:entry", ATOM_NS):
            authors = [
                normalize_whitespace(author.findtext("a:name", default="", namespaces=ATOM_NS))
                for author in entry.findall("a:author", ATOM_NS)
            ]
            pdf_url = None
            for link in entry.findall("a:link", ATOM_NS):
                if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                    pdf_url = link.attrib.get("href")
                    break
            published = normalize_whitespace(entry.findtext("a:published", default="", namespaces=ATOM_NS))
            article_id = normalize_whitespace(entry.findtext("a:id", default="", namespaces=ATOM_NS))
            results.append(
                LiteratureResult(
                    title=normalize_whitespace(entry.findtext("a:title", default="", namespaces=ATOM_NS)),
                    abstract=normalize_whitespace(entry.findtext("a:summary", default="", namespaces=ATOM_NS)),
                    authors=[author for author in authors if author],
                    year=year_from_any(published),
                    published_date=published,
                    source=self.name,
                    source_id=article_id,
                    landing_url=article_id,
                    pdf_url=pdf_url,
                    extras={},
                )
            )
        return results
