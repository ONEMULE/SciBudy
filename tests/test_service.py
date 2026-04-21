import time

from research_mcp.errors import ProviderRequestError
from research_mcp.models import AnalysisSummaryResponse, IngestResponse, LiteratureResult
from research_mcp.utils import now_utc_iso
from research_mcp.service import ResearchService
from research_mcp.settings import Settings


class StubProvider:
    def __init__(self, name, results=None, error=None, ready=True, message=None, delay=0.0):
        self.name = name
        self._results = results or []
        self._error = error
        self._ready = ready
        self._message = message
        self._delay = delay

    def ready(self):
        return self._ready, self._message

    def search(self, query, limit, sort):
        if self._delay:
            time.sleep(self._delay)
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
    assert all(item.elapsed_ms is None or item.elapsed_ms >= 0 for item in response.provider_coverage)
    assert response.results[0].title == "Useful paper"


def test_service_times_out_slow_provider_without_losing_fast_results(tmp_path):
    fast_provider = StubProvider(
        "OpenAlex",
        results=[LiteratureResult(title="Fast calibration paper", source="OpenAlex", source_id="W1")],
    )
    slow_provider = StubProvider("CORE", results=[LiteratureResult(title="Slow paper", source="CORE", source_id="C1")], delay=0.15)
    service = ResearchService(
        settings=Settings(
            RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db"),
            RESEARCH_MCP_PROVIDER_TIMEOUT_SEC=0.05,
            RESEARCH_MCP_SEARCH_TOTAL_TIMEOUT_SEC=0.05,
        ),
        providers={"openalex": fast_provider, "core": slow_provider},
        oa_resolver=StubResolver(),
    )

    response = service._run_provider_group(
        query="simulation based calibration",
        provider_names=["openalex", "core"],
        mode="general",
        limit=5,
        sort="relevance",
    )

    assert response.result_count == 1
    assert response.results[0].title == "Fast calibration paper"
    assert any(item.provider == "CORE" and item.status == "error" and "timed out" in (item.message or "") for item in response.provider_coverage)


def test_resolve_open_access_reports_configuration_error(tmp_path):
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={},
        oa_resolver=StubResolver(),
    )

    response = service.resolve_open_access("10.1000/example")

    assert response.status == "error"
    assert response.message == "missing UNPAYWALL_EMAIL"


def test_research_workflow_collects_library_without_ingest(tmp_path):
    provider = StubProvider(
        "OpenAlex",
        results=[LiteratureResult(title="Workflow Paper", source="OpenAlex", source_id="W1", year=2026)],
    )
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={"openalex": provider},
        oa_resolver=StubResolver(),
    )

    response = service.research_workflow(
        query="workflow paper",
        limit=1,
        target_dir=str(tmp_path / "workflow-library"),
        download_pdfs=False,
        ingest=False,
        synthesize=True,
    )

    assert response.status == "partial"
    assert response.library_id
    assert response.counts["search_results"] == 1
    assert response.ingest_status == "skipped"
    assert response.synthesis_status == "skipped"
    assert any("ingest=false" in warning for warning in response.warnings)
    assert any("ingest_library" in action for action in response.next_actions)
    assert response.workflow_stage == "organized"
    assert response.metrics["total_elapsed_ms"] >= 0
    assert response.step_results["search"]["result_count"] == 1


def test_research_workflow_dry_run_has_no_side_effects(tmp_path):
    provider = StubProvider(
        "OpenAlex",
        results=[LiteratureResult(title="Workflow Paper", source="OpenAlex", source_id="W1", year=2026)],
    )
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={"openalex": provider},
        oa_resolver=StubResolver(),
    )
    target_dir = tmp_path / "dry-run-library"

    response = service.research_workflow(
        query="workflow paper",
        limit=1,
        target_dir=str(target_dir),
        dry_run=True,
    )

    assert response.status == "ok"
    assert response.dry_run is True
    assert response.workflow_stage == "planned"
    assert response.planned_steps == ["search", "organize", "download", "ingest", "synthesize"]
    assert not target_dir.exists()
    assert response.step_results["plan"]["will_write_files"] is False


def test_research_workflow_fast_mode_skips_ingest_and_synthesis(tmp_path):
    provider = StubProvider(
        "OpenAlex",
        results=[LiteratureResult(title="Workflow Paper", source="OpenAlex", source_id="W1", year=2026)],
    )
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={"openalex": provider},
        oa_resolver=StubResolver(),
    )

    response = service.research_workflow(
        query="workflow paper",
        limit=1,
        target_dir=str(tmp_path / "fast-library"),
        download_pdfs=False,
        quality_mode="fast",
    )

    assert response.status == "ok"
    assert response.quality_mode == "fast"
    assert response.ingest_status == "skipped"
    assert response.synthesis_status is None
    assert response.workflow_stage == "organized"
    assert response.planned_steps == ["search", "organize"]


def test_research_workflow_runs_ingest_and_synthesis_when_ready(tmp_path):
    provider = StubProvider(
        "OpenAlex",
        results=[LiteratureResult(title="Workflow Paper", source="OpenAlex", source_id="W1", year=2026)],
    )
    service = ResearchService(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        providers={"openalex": provider},
        oa_resolver=StubResolver(),
    )

    def fake_ingest(library_id, include_forums=True, reingest=False):
        return IngestResponse(
            status="ok",
            generated_at=now_utc_iso(),
            library_id=library_id,
            mode="hybrid",
            compute_backend="local",
            processed_count=1,
            ready_count=1,
        )

    def fake_synthesis(library_id, topic, max_items=50, profile="auto"):
        return AnalysisSummaryResponse(
            status="ok",
            generated_at=now_utc_iso(),
            library_id=library_id,
            topic=topic,
            analysis_mode="hybrid",
            compute_backend="local",
            title="Workflow synthesis",
            summary="Synthesis complete.",
            report_id="report1",
            report_path=str(tmp_path / "report.md"),
        )

    service.ingest_library = fake_ingest
    service.build_research_synthesis = fake_synthesis

    response = service.research_workflow(
        query="workflow paper",
        limit=1,
        target_dir=str(tmp_path / "workflow-ready"),
        download_pdfs=False,
        ingest=True,
        synthesize=True,
        topic="workflow topic",
        profile="general",
    )

    assert response.status == "ok"
    assert response.ingest_status == "ok"
    assert response.synthesis_status == "ok"
    assert response.synthesis_report_id == "report1"
    assert response.synthesis_summary == "Synthesis complete."
    assert response.workflow_stage == "synthesized"
    assert response.step_results["synthesize"]["report_id"] == "report1"
    assert response.metrics["synthesis_elapsed_ms"] >= 0
    assert response.quality_summary["status"] == "ok"
    assert any("read_synthesis_report" in action for action in response.next_actions)
