from __future__ import annotations

from research_mcp.models import OpenAccessResponse
from research_mcp.providers.base import BaseProvider
from research_mcp.utils import canonical_doi


class UnpaywallProvider(BaseProvider):
    name = "Unpaywall"
    cache_ttl_sec = 24 * 60 * 60
    min_interval_sec = 1.0
    required_settings = (("UNPAYWALL_EMAIL", "unpaywall_email"),)

    def search(self, query: str, limit: int, sort: str):  # pragma: no cover - not part of this provider
        raise NotImplementedError

    def resolve(self, doi: str) -> OpenAccessResponse:
        data, _ = self.client.get_json(
            provider_name=self.name,
            url=f"https://api.unpaywall.org/v2/{canonical_doi(doi)}",
            params={"email": self.settings.unpaywall_email},
            ttl_sec=self.cache_ttl_sec,
            min_interval_sec=self.min_interval_sec,
        )
        best = data.get("best_oa_location") or {}
        return OpenAccessResponse(
            status="ok",
            doi=canonical_doi(doi) or doi,
            is_open_access=data.get("is_oa"),
            best_url=best.get("landing_page_url") or best.get("url"),
            pdf_url=best.get("url_for_pdf"),
            license=best.get("license"),
            oa_status=data.get("oa_status"),
            journal_is_in_doaj=data.get("journal_is_in_doaj"),
            extras={
                "genre": data.get("genre"),
                "host_type": best.get("host_type"),
                "version": best.get("version"),
            },
        )
