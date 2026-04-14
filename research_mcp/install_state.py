from __future__ import annotations

import json
import platform
from typing import Any

from pydantic import BaseModel, Field

from research_mcp import __version__
from research_mcp.paths import APP_HOME, INSTALL_STATE_FILE, python_path
from research_mcp.utils import now_utc_iso


class LocalModelState(BaseModel):
    profile: str = "qwen4b"
    env_name: str | None = None
    embedding_model: str | None = None
    reranker_model: str | None = None
    installed: bool = False
    warmed_embedding: bool = False
    warmed_reranker: bool = False
    notes: list[str] = Field(default_factory=list)


class InstallState(BaseModel):
    version: str = __version__
    updated_at: str = Field(default_factory=now_utc_iso)
    app_home: str = str(APP_HOME)
    platform: str = platform.system().lower()
    install_profile: str = "base"
    runtime_python: str = str(python_path())
    runtime_command: str = ""
    codex_configured: bool = False
    doctor_status: str | None = None
    ui_assets_ready: bool = False
    notes: list[str] = Field(default_factory=list)
    local_models: LocalModelState = Field(default_factory=LocalModelState)


def load_install_state() -> InstallState:
    if not INSTALL_STATE_FILE.exists():
        return InstallState()
    try:
        payload = json.loads(INSTALL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return InstallState()
    return InstallState.model_validate(payload)


def save_install_state(state: InstallState) -> InstallState:
    INSTALL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_STATE_FILE.write_text(
        json.dumps(state.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return state


def update_install_state(**updates: Any) -> InstallState:
    state = load_install_state()
    payload = state.model_dump(mode="python")
    payload.update({key: value for key, value in updates.items() if value is not None})
    payload["updated_at"] = now_utc_iso()
    next_state = InstallState.model_validate(payload)
    return save_install_state(next_state)
