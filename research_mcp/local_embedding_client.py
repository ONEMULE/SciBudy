from __future__ import annotations

import json
import subprocess
import threading
from pathlib import Path

from research_mcp.paths import PACKAGE_DIR
from research_mcp.settings import Settings


CONDA_ENVS_DIR = Path.home() / "anaconda3" / "envs"
WORKER_SCRIPT = PACKAGE_DIR / "local_embedding_worker.py"


class LocalEmbeddingClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._proc: subprocess.Popen[str] | None = None
        self._lock = threading.Lock()
        self._disabled_reason: str | None = None

    @property
    def disabled_reason(self) -> str | None:
        return self._disabled_reason

    def is_configured(self) -> bool:
        if self.settings.local_embedding_model.strip().lower() == "hash-embedding-v1":
            return False
        env_python = CONDA_ENVS_DIR / self.settings.local_embedding_env / "bin" / "python"
        return self._disabled_reason is None and env_python.exists()

    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def embed(self, texts: list[str], *, input_type: str) -> list[list[float]] | None:
        if not texts:
            return []
        with self._lock:
            if not self._ensure_started():
                return None
            assert self._proc is not None
            payload = {"action": "embed", "texts": texts, "input_type": input_type}
            try:
                self._proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
                self._proc.stdin.flush()
                line = self._proc.stdout.readline()
            except Exception as exc:  # noqa: BLE001
                self._disabled_reason = str(exc)
                self.close()
                return None
        if not line:
            self._disabled_reason = "local embedding worker stopped"
            self.close()
            return None
        response = json.loads(line)
        if response.get("status") != "ok":
            self._disabled_reason = response.get("message") or "local embedding worker error"
            self.close()
            return None
        return response.get("vectors") or None

    def close(self) -> None:
        with self._lock:
            if self._proc is not None:
                try:
                    self._proc.terminate()
                except Exception:  # noqa: BLE001
                    pass
                self._proc = None

    def _ensure_started(self) -> bool:
        if self._disabled_reason is not None:
            return False
        if self._proc is not None and self._proc.poll() is None:
            return True
        env_python = CONDA_ENVS_DIR / self.settings.local_embedding_env / "bin" / "python"
        if not env_python.exists():
            self._disabled_reason = f"local embedding env python not found: {env_python}"
            return False
        try:
            self._proc = subprocess.Popen(
                [
                    str(env_python),
                    "-u",
                    str(WORKER_SCRIPT),
                    "--model",
                    self.settings.local_embedding_model,
                    "--output-dim",
                    str(int(self.settings.local_embedding_dimension)),
                    "--max-length",
                    "4096",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            assert self._proc.stdout is not None
            line = self._proc.stdout.readline()
        except Exception as exc:  # noqa: BLE001
            self._disabled_reason = str(exc)
            self._proc = None
            return False
        if not line:
            self._disabled_reason = "local embedding worker failed to start"
            self.close()
            return False
        response = json.loads(line)
        if response.get("status") != "ready":
            self._disabled_reason = response.get("message") or "local embedding worker failed to initialize"
            self.close()
            return False
        return True
