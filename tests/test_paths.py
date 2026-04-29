from research_mcp import paths


def test_resolve_app_home_ignores_source_venv_and_empty_state(tmp_path, monkeypatch):
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / ".venv").mkdir()
    (project_root / "state").mkdir()
    default_home = tmp_path / "home" / ".research-mcp"
    monkeypatch.setattr(paths, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(paths, "DEFAULT_APP_HOME", default_home)
    monkeypatch.delenv("RESEARCH_MCP_HOME", raising=False)
    monkeypatch.delenv("SCIBUDY_HOME", raising=False)

    assert paths._resolve_app_home() == default_home


def test_resolve_app_home_preserves_non_empty_legacy_state(tmp_path, monkeypatch):
    project_root = tmp_path / "repo"
    state_dir = project_root / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "research.db").write_text("", encoding="utf-8")
    default_home = tmp_path / "home" / ".research-mcp"
    monkeypatch.setattr(paths, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(paths, "DEFAULT_APP_HOME", default_home)
    monkeypatch.delenv("RESEARCH_MCP_HOME", raising=False)
    monkeypatch.delenv("SCIBUDY_HOME", raising=False)

    assert paths._resolve_app_home() == project_root
