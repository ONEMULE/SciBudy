from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from research_mcp.paths import STATE_DIR
from research_mcp.utils import now_utc_iso


RUNS_DIR = STATE_DIR / "runs"


def ensure_runs_dir() -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return RUNS_DIR


def save_run(kind: str, payload: dict[str, Any], *, summary: dict[str, Any]) -> Path:
    runs_dir = ensure_runs_dir()
    slug = _slugify(str(summary.get("query") or summary.get("doi") or kind))
    timestamp = now_utc_iso().replace(":", "").replace("-", "").replace("+00:00", "Z")
    path = runs_dir / f"{timestamp}-{kind}-{slug}.json"
    document = {
        "kind": kind,
        "saved_at": now_utc_iso(),
        "summary": summary,
        "payload": payload,
    }
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    runs_dir = ensure_runs_dir()
    items = sorted(runs_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    results: list[dict[str, Any]] = []
    for path in items[:limit]:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        summary = document.get("summary") or {}
        results.append(
            {
                "id": path.stem,
                "path": str(path),
                "kind": document.get("kind"),
                "saved_at": document.get("saved_at"),
                "query": summary.get("query"),
                "doi": summary.get("doi"),
                "result_count": summary.get("result_count"),
            }
        )
    return results


def load_run(identifier: str) -> dict[str, Any]:
    runs_dir = ensure_runs_dir()
    if identifier == "latest":
        runs = list_runs(limit=1)
        if not runs:
            raise FileNotFoundError("No saved runs found.")
        return json.loads(Path(runs[0]["path"]).read_text(encoding="utf-8"))

    path = Path(identifier)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    matches = sorted(runs_dir.glob(f"{identifier}*.json"))
    if not matches:
        raise FileNotFoundError(f"No saved run matching {identifier!r}.")
    return json.loads(matches[-1].read_text(encoding="utf-8"))


def _slugify(value: str) -> str:
    compact = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return compact[:60] or "run"
