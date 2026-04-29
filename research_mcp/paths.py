from __future__ import annotations

import os
import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent if (PACKAGE_DIR.parent / "pyproject.toml").exists() else PACKAGE_DIR
DEFAULT_APP_HOME = Path.home() / ".research-mcp"
CODEX_CONFIG_FILE = Path.home() / ".codex" / "config.toml"


def _resolve_app_home() -> Path:
    override = os.getenv("RESEARCH_MCP_HOME") or os.getenv("SCIBUDY_HOME")
    if override:
        return Path(override).expanduser().resolve()

    legacy_files = [PROJECT_ROOT / ".env"]
    legacy_dirs = [PROJECT_ROOT / "state", PROJECT_ROOT / "analysis", PROJECT_ROOT / "library"]
    has_legacy_dir_data = any(path.exists() and any(path.iterdir()) for path in legacy_dirs)
    if any(path.exists() for path in legacy_files) or has_legacy_dir_data:
        return PROJECT_ROOT
    return DEFAULT_APP_HOME


APP_HOME = _resolve_app_home()
APP_HOME.mkdir(parents=True, exist_ok=True)
STATE_DIR = APP_HOME / "state"
LIBRARY_DIR = APP_HOME / "library"
ANALYSIS_DIR = APP_HOME / "analysis"
ENV_FILE = APP_HOME / ".env"
ENV_EXAMPLE_FILE = PROJECT_ROOT / ".env.example"
INSTALL_STATE_FILE = STATE_DIR / "install_state.json"
RUNTIME_DIR = APP_HOME / "runtime"
RUNTIME_VENV_DIR = RUNTIME_DIR / ".venv"
UI_ASSETS_DIR = APP_HOME / "ui" / "dist"
LOGS_DIR = STATE_DIR / "logs"
RELEASE_MANIFEST_FILE = (
    PROJECT_ROOT / "release-manifest.json"
    if (PROJECT_ROOT / "release-manifest.json").exists()
    else PACKAGE_DIR / "release-manifest.json"
)


def command_path() -> Path:
    script_name = "research-mcp.exe" if os.name == "nt" else "research-mcp"
    prefix_bin = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin") / script_name
    if prefix_bin.exists():
        return prefix_bin.resolve()
    candidate = Path(sys.executable).resolve().with_name(script_name)
    if candidate.exists():
        return candidate
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "research-mcp.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "research-mcp"


def python_path() -> Path:
    candidate = Path(sys.executable)
    if candidate.exists():
        return candidate
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"
