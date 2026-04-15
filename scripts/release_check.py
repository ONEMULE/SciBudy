from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    package_json = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert manifest["python"]["package_name"] == "scibudy"
    assert f'name = "{manifest["python"]["package_name"]}"' in pyproject
    assert package_json["name"] == "scibudy-installer"
    assert manifest["installer_version"] == package_json["version"]
    assert manifest["python"]["version"] in pyproject
    assert (ROOT / "README.md").exists()
    assert (ROOT / "LICENSE").exists()
    assert (ROOT / "docs" / "en").exists()
    assert (ROOT / "docs" / "zh").exists()
    print("release-check: ok")


if __name__ == "__main__":
    main()
