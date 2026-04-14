from research_mcp.errors import ProviderRequestError
from research_mcp.models import LiteratureResult
from research_mcp.service import ResearchService
from research_mcp.settings import Settings


class StubProvider:
    def __init__(self, name, results=None, error=None, ready=True, message=None):
        self.name = name
        self._results = results or []
        self._error = error
        self._ready = ready
        self._message = message

    def ready(self):
        return self._ready, self._message

    def search(self, query, limit, sort):
        if self._error:
            raise self._error
        return self._results


class StubResolver:
    def ready(self):
        return False, "missing UNPAYWALL_EMAIL"


def test_service_returns_partial_results_when_one_provider_fails(tmp_path):
    ok_provider = StubProvider(
        "OpenAlex",
        results=[
            LiteratureResult(
                title="Useful paper",
                source="OpenAlex",
                source_id="W1",
                year=2025,
            )
        ],
    )
    failing_provider = StubProvider("Crossref", error=ProviderRequestError("boom"))
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={"openalex": ok_provider, "crossref": failing_provider},
        oa_resolver=StubResolver(),
    )

    response = service._run_provider_group(
        query="useful paper",
        provider_names=["openalex", "crossref"],
        mode="general",
        limit=5,
        sort="relevance",
    )

    assert response.result_count == 1
    assert any(item.status == "error" and item.provider == "Crossref" for item in response.provider_coverage)
    assert response.results[0].title == "Useful paper"


def test_resolve_open_access_reports_configuration_error(tmp_path):
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={},
        oa_resolver=StubResolver(),
    )

    response = service.resolve_open_access("10.1000/example")

    assert response.status == "error"
    assert response.message == "missing UNPAYWALL_EMAIL"
