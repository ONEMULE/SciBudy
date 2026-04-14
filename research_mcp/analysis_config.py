from __future__ import annotations

from dotenv import dotenv_values

from research_mcp.models import AnalysisSettingsResponse
from research_mcp.paths import ENV_FILE
from research_mcp.settings import Settings, get_settings
from research_mcp.utils import now_utc_iso


SETTINGS_KEYS = {
    "analysis_mode": "RESEARCH_MCP_ANALYSIS_MODE",
    "compute_backend": "RESEARCH_MCP_COMPUTE_BACKEND",
    "chunk_size": "RESEARCH_MCP_CHUNK_SIZE",
    "chunk_overlap": "RESEARCH_MCP_CHUNK_OVERLAP",
    "max_summary_depth": "RESEARCH_MCP_MAX_SUMMARY_DEPTH",
    "forum_enrichment_enabled": "RESEARCH_MCP_FORUM_ENRICHMENT_ENABLED",
    "forum_source_profile": "RESEARCH_MCP_FORUM_SOURCE_PROFILE",
    "forum_sources": "RESEARCH_MCP_FORUM_SOURCES",
    "openai_embedding_model": "RESEARCH_MCP_OPENAI_EMBEDDING_MODEL",
    "openai_summary_model": "RESEARCH_MCP_OPENAI_SUMMARY_MODEL",
    "local_embedding_model": "RESEARCH_MCP_LOCAL_EMBEDDING_MODEL",
    "local_embedding_dimension": "RESEARCH_MCP_LOCAL_EMBEDDING_DIMENSION",
    "local_embedding_env": "RESEARCH_MCP_LOCAL_EMBEDDING_ENV",
    "local_reranker_model": "RESEARCH_MCP_LOCAL_RERANKER_MODEL",
    "local_reranker_env": "RESEARCH_MCP_LOCAL_RERANKER_ENV",
}


def settings_response(settings: Settings | None = None, *, message: str | None = None) -> AnalysisSettingsResponse:
    settings = settings or get_settings()
    return AnalysisSettingsResponse(
        status="ok",
        generated_at=now_utc_iso(),
        analysis_mode=settings.analysis_mode if settings.analysis_mode in {"rules", "hybrid", "semantic_heavy"} else "hybrid",
        compute_backend=settings.compute_backend if settings.compute_backend in {"auto", "local", "openai"} else "auto",
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        max_summary_depth=settings.max_summary_depth if settings.max_summary_depth in {"shallow", "standard", "deep"} else "standard",
        forum_enrichment_enabled=settings.forum_enrichment_enabled,
        forum_source_profile=settings.forum_source_profile if settings.forum_source_profile in {"high_trust", "extended", "experimental"} else "high_trust",
        forum_sources=[part.strip() for part in settings.forum_sources.split(",") if part.strip()],
        openai_embedding_model=settings.openai_embedding_model,
        openai_summary_model=settings.openai_summary_model,
        local_embedding_model=settings.local_embedding_model,
        local_embedding_dimension=settings.local_embedding_dimension,
        local_embedding_env=settings.local_embedding_env,
        local_reranker_model=settings.local_reranker_model,
        local_reranker_env=settings.local_reranker_env,
        openai_ready=bool(settings.openai_api_key),
        message=message,
    )


def update_settings(**updates) -> AnalysisSettingsResponse:
    current = dict(dotenv_values(ENV_FILE))
    for key, value in updates.items():
        if value is None or key not in SETTINGS_KEYS:
            continue
        env_key = SETTINGS_KEYS[key]
        if isinstance(value, bool):
            current[env_key] = "true" if value else "false"
        else:
            current[env_key] = str(value)
    lines = []
    for key, value in current.items():
        if value is None:
            continue
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    get_settings.cache_clear()
    return settings_response(message="analysis settings updated")
