from __future__ import annotations

from research_mcp.client import ResearchHttpClient
from research_mcp.providers.arxiv import ArxivProvider
from research_mcp.providers.core import COREProvider
from research_mcp.providers.crossref import CrossrefProvider
from research_mcp.providers.doaj import DOAJProvider
from research_mcp.providers.europepmc import EuropePMCProvider
from research_mcp.providers.openalex import OpenAlexProvider
from research_mcp.providers.pubmed import PubMedProvider
from research_mcp.providers.semanticscholar import SemanticScholarProvider
from research_mcp.providers.unpaywall import UnpaywallProvider
from research_mcp.settings import Settings


def build_providers(settings: Settings, client: ResearchHttpClient):
    providers = {
        "arxiv": ArxivProvider(settings, client),
        "openalex": OpenAlexProvider(settings, client),
        "crossref": CrossrefProvider(settings, client),
        "semanticscholar": SemanticScholarProvider(settings, client),
        "pubmed": PubMedProvider(settings, client),
        "europepmc": EuropePMCProvider(settings, client),
        "doaj": DOAJProvider(settings, client),
        "core": COREProvider(settings, client),
    }
    resolver = UnpaywallProvider(settings, client)
    return providers, resolver
