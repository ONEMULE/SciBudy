from __future__ import annotations

import mimetypes
import re
from pathlib import Path

from research_mcp.paths import PROJECT_ROOT, UI_ASSETS_DIR


WEB_DIR = PROJECT_ROOT / "web"
DIST_DIR = WEB_DIR / "dist"
UI_TEMPLATE_URI = "ui://widget/library-manager-v1.html"


def runtime_dist_dir() -> Path:
    return UI_ASSETS_DIR if (UI_ASSETS_DIR / "index.html").exists() else DIST_DIR


def ui_build_exists() -> bool:
    return (runtime_dist_dir() / "index.html").exists()


def load_local_index_html() -> str:
    if not ui_build_exists():
        return _missing_html()
    return (runtime_dist_dir() / "index.html").read_text(encoding="utf-8")


def load_widget_html() -> str:
    if not ui_build_exists():
        return _missing_html()
    dist_dir = runtime_dist_dir()
    html = (dist_dir / "index.html").read_text(encoding="utf-8")
    css_links = re.findall(r'<link[^>]+href="([^"]+\.css)"[^>]*>', html)
    js_links = re.findall(r'<script[^>]+src="([^"]+\.js)"[^>]*></script>', html)
    for href in css_links:
        asset_path = _asset_path(href, dist_dir=dist_dir)
        css = asset_path.read_text(encoding="utf-8")
        html = html.replace(f'<link rel="stylesheet" crossorigin href="{href}">', f"<style>{css}</style>")
    for src in js_links:
        asset_path = _asset_path(src, dist_dir=dist_dir)
        js = asset_path.read_text(encoding="utf-8")
        html = re.sub(rf'<script[^>]+src="{re.escape(src)}"[^>]*></script>', f"<script type=\"module\">{js}</script>", html, count=1)
    return html


def load_asset(path_fragment: str) -> tuple[bytes, str]:
    dist_dir = runtime_dist_dir()
    asset_path = (dist_dir / path_fragment).resolve()
    if not str(asset_path).startswith(str(dist_dir.resolve())) or not asset_path.exists():
        raise FileNotFoundError(path_fragment)
    mime_type = mimetypes.guess_type(asset_path.name)[0] or "application/octet-stream"
    return asset_path.read_bytes(), mime_type


def _asset_path(asset_url: str, *, dist_dir: Path) -> Path:
    cleaned = asset_url.lstrip("/")
    if cleaned.startswith("app/"):
        cleaned = cleaned[len("app/") :]
    return (dist_dir / cleaned).resolve()


def _missing_html() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Research MCP UI Not Built</title>
    <style>
      body { font-family: system-ui, sans-serif; padding: 32px; background: #f5f7fb; color: #17212b; }
      code { background: #e8edf7; padding: 2px 6px; border-radius: 6px; }
      .card { max-width: 760px; background: white; border-radius: 16px; padding: 24px; box-shadow: 0 8px 24px rgba(0,0,0,.08); }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Research MCP UI is not built yet</h1>
      <p>Run <code>cd ~/.mcp/research/web && npm install && npm run build</code>, then restart the HTTP server.</p>
    </div>
  </body>
</html>
""".strip()
