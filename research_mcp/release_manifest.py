from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from research_mcp import __version__
from research_mcp.paths import RELEASE_MANIFEST_FILE


class PythonArtifact(BaseModel):
    package_name: str = "scibudy"
    version: str = __version__
    requirement: str = f"scibudy=={__version__}"


class FrontendArtifact(BaseModel):
    source_dir: str = "web"
    dist_dir: str = "web/dist"


class ReleaseManifest(BaseModel):
    installer_version: str = __version__
    python: PythonArtifact = Field(default_factory=PythonArtifact)
    frontend: FrontendArtifact = Field(default_factory=FrontendArtifact)
    install_profiles: dict[str, dict[str, Any]] = Field(
        default_factory=lambda: {
            "base": {"codex": True, "doctor": True, "sync_ui": True},
            "analysis": {"codex": True, "doctor": True, "sync_ui": True},
            "gpu-local": {"codex": True, "doctor": True, "sync_ui": True, "install_local_models": True, "warm_local_models": True},
            "full": {"codex": True, "doctor": True, "sync_ui": True, "install_local_models": True, "warm_local_models": True},
        }
    )
    local_model_profile: dict[str, Any] = Field(
        default_factory=lambda: {
            "name": "qwen4b",
            "embedding_model": "Qwen/Qwen3-Embedding-4B",
            "reranker_model": "Qwen/Qwen3-Reranker-4B",
            "env_name": "research_embed",
            "embedding_dimension": 2560,
        }
    )


def load_release_manifest(path: Path | None = None) -> ReleaseManifest:
    manifest_path = path or RELEASE_MANIFEST_FILE
    if not manifest_path.exists():
        return ReleaseManifest()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return ReleaseManifest.model_validate(payload)


def write_release_manifest(path: Path | None = None) -> Path:
    manifest_path = path or RELEASE_MANIFEST_FILE
    manifest = ReleaseManifest()
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path
