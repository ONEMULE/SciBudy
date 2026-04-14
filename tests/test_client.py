import httpx

from research_mcp.cache import SQLiteStateStore
from research_mcp.client import ResearchHttpClient
from research_mcp.rate_limit import RateLimiter
from research_mcp.settings import Settings


def test_http_client_uses_cache(tmp_path):
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(200, json={"ok": True, "url": str(request.url)})

    state = SQLiteStateStore(tmp_path / "state.db")
    client = ResearchHttpClient(
        settings=Settings(RESEARCH_MCP_CACHE_DB_PATH=str(tmp_path / "state.db")),
        state=state,
        rate_limiter=RateLimiter(state),
        transport=httpx.MockTransport(handler),
    )

    first, first_cached = client.get_json(
        provider_name="Test",
        url="https://example.com/search",
        params={"q": "quantum"},
        ttl_sec=60,
        min_interval_sec=0,
    )
    second, second_cached = client.get_json(
        provider_name="Test",
        url="https://example.com/search",
        params={"q": "quantum"},
        ttl_sec=60,
        min_interval_sec=0,
    )

    assert first["ok"] is True
    assert second["ok"] is True
    assert first_cached is False
    assert second_cached is True
    assert calls["count"] == 1
