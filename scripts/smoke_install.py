from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-path", default=str(ROOT))
    parser.add_argument("--profile", default="base")
    args = parser.parse_args()

    tmp_root = Path(tempfile.mkdtemp(prefix="scibudy-smoke-"))
    try:
        subprocess.run(
            [
                "node",
                str(ROOT / "bin" / "scibudy-install.mjs"),
                "--from-path",
                str(Path(args.from_path).resolve()),
                "--profile",
                args.profile,
                "--no-prompt",
                "--no-install-codex",
                "--app-home",
                str(tmp_root),
            ],
            check=True,
        )
        assert (tmp_root / "state" / "install_state.json").exists()
        assert (tmp_root / "ui" / "dist" / "index.html").exists()
        print(f"smoke-install: ok ({tmp_root})")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
