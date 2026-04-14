from research_mcp.service import ResearchService
from research_mcp.settings import Settings


class StubProvider:
    def __init__(self, name, enabled_flag="", required_settings=(), ready=True, message=None):
        self.name = name
        self.enabled_flag = enabled_flag
        self.required_settings = required_settings
        self._ready = ready
        self._message = message

    def ready(self):
        return self._ready, self._message


class StubResolver:
    name = "Unpaywall"
    required_settings = (("UNPAYWALL_EMAIL", "unpaywall_email"),)

    def ready(self):
        return False, "missing UNPAYWALL_EMAIL"


def test_health_check_reports_missing_credentials(tmp_path):
    settings = Settings(
        RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db"),
        CORE_API_KEY="",
        UNPAYWALL_EMAIL="",
    )
    service = ResearchService(
        settings=settings,
        providers={
            "core": StubProvider(
                "CORE",
                enabled_flag="enable_core",
                required_settings=(("CORE_API_KEY", "core_api_key"),),
                ready=False,
                message="missing CORE_API_KEY",
            )
        },
        oa_resolver=StubResolver(),
    )

    health = service.health_check()

    assert health.status == "degraded"
    assert any(item.provider == "CORE" and item.missing_credentials == ["CORE_API_KEY"] for item in health.provider_statuses)
    assert any(item.provider == "Unpaywall" and item.missing_credentials == ["UNPAYWALL_EMAIL"] for item in health.provider_statuses)


def test_health_check_does_not_degrade_for_ready_public_provider(tmp_path):
    settings = Settings(
        RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db"),
        SEMANTIC_SCHOLAR_API_KEY="",
        UNPAYWALL_EMAIL="configured@example.com",
    )
    service = ResearchService(
        settings=settings,
        providers={
            "semanticscholar": StubProvider(
                "Semantic Scholar",
                enabled_flag="enable_semantic_scholar",
                required_settings=(("SEMANTIC_SCHOLAR_API_KEY", "semantic_scholar_api_key"),),
                ready=True,
                message="using public shared pool via bulk search",
            )
        },
        oa_resolver=type(
            "ReadyResolver",
            (),
            {
                "name": "Unpaywall",
                "required_settings": (("UNPAYWALL_EMAIL", "unpaywall_email"),),
                "ready": staticmethod(lambda: (True, None)),
            },
        )(),
    )

    health = service.health_check()

    assert health.status == "ok"
    assert any(
        item.provider == "Semantic Scholar"
        and item.ready is True
        and item.missing_credentials == ["SEMANTIC_SCHOLAR_API_KEY"]
        for item in health.provider_statuses
    )
    assert not any("SEMANTIC_SCHOLAR_API_KEY" in suggestion for suggestion in health.suggestions)
