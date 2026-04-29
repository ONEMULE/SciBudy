from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SITE_URL = "https://onemule.github.io/SciBudy/"


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads(read_text(relative_path))


def load_pyproject() -> dict[str, Any]:
    text = read_text("pyproject.toml")
    if tomllib is not None:
        return tomllib.loads(text)

    project = {
        "name": _find_required_value(text, r'(?m)^name\s*=\s*"([^"]+)"'),
        "version": _find_required_value(text, r'(?m)^version\s*=\s*"([^"]+)"'),
        "urls": {
            "Homepage": _find_required_value(text, r'(?m)^Homepage\s*=\s*"([^"]+)"'),
            "Documentation": _find_required_value(text, r'(?m)^Documentation\s*=\s*"([^"]+)"'),
        },
    }
    return {"project": project}


def _find_required_value(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1) if match else None


def add_equal_check(
    failures: list[str],
    location: str,
    actual: object,
    expected: object,
    description: str,
) -> None:
    if actual != expected:
        failures.append(
            f"{location}: {description} is {actual!r}, expected {expected!r}"
        )


def add_site_url_checks(
    failures: list[str],
    relative_path: str,
    pattern: str,
    description: str,
) -> None:
    matches = re.findall(pattern, read_text(relative_path))
    if not matches:
        failures.append(f"{relative_path}: could not find {description}")
        return
    for index, url in enumerate(matches, start=1):
        location = relative_path if len(matches) == 1 else f"{relative_path} #{index}"
        add_equal_check(failures, location, url, CANONICAL_SITE_URL, description)


def add_version_consistency_checks(
    failures: list[str],
    pyproject: dict[str, Any],
    package_json: dict[str, Any],
    root_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
) -> None:
    project = pyproject.get("project", {})
    init_version = _find_required_value(
        read_text("research_mcp/__init__.py"),
        r'(?m)^__version__\s*=\s*"([^"]+)"',
    )
    versions = [
        ("pyproject.toml: project.version", project.get("version")),
        ("package.json: version", package_json.get("version")),
        (
            "release-manifest.json: installer_version",
            root_manifest.get("installer_version"),
        ),
        (
            "release-manifest.json: python.version",
            root_manifest.get("python", {}).get("version"),
        ),
        (
            "research_mcp/release-manifest.json: installer_version",
            package_manifest.get("installer_version"),
        ),
        (
            "research_mcp/release-manifest.json: python.version",
            package_manifest.get("python", {}).get("version"),
        ),
        ("research_mcp/__init__.py: __version__", init_version),
    ]
    missing = [location for location, version in versions if version is None]
    for location in missing:
        failures.append(f"{location}: version is missing")

    present_versions = [
        (location, version) for location, version in versions if version is not None
    ]
    distinct_versions = {version for _, version in present_versions}
    if len(distinct_versions) <= 1:
        return

    expected = present_versions[0][1]
    for location, version in present_versions:
        failures.append(
            f"{location}: version is {version!r}; expected all versions to match {expected!r}"
        )


def main() -> None:
    root_manifest = load_json("release-manifest.json")
    package_manifest = load_json("research_mcp/release-manifest.json")
    pyproject = load_pyproject()
    project = pyproject.get("project", {})
    project_urls = project.get("urls", {})
    package_json = load_json("package.json")

    failures: list[str] = []

    add_equal_check(
        failures,
        "release-manifest.json: python.package_name",
        root_manifest.get("python", {}).get("package_name"),
        "scibudy",
        "Python package name",
    )
    add_equal_check(
        failures,
        "pyproject.toml: project.name",
        project.get("name"),
        "scibudy",
        "Python project name",
    )
    add_equal_check(
        failures,
        "package.json: name",
        package_json.get("name"),
        "scibudy-installer",
        "npm package name",
    )

    add_version_consistency_checks(
        failures, pyproject, package_json, root_manifest, package_manifest
    )

    for manifest_path, manifest in [
        ("release-manifest.json", root_manifest),
        ("research_mcp/release-manifest.json", package_manifest),
    ]:
        python_package = manifest.get("python", {}).get("package_name")
        python_version = manifest.get("python", {}).get("version")
        add_equal_check(
            failures,
            f"{manifest_path}: python.requirement",
            manifest.get("python", {}).get("requirement"),
            f"{python_package}=={python_version}",
            "Python requirement",
        )

    add_equal_check(
        failures,
        "pyproject.toml: [project.urls].Homepage",
        project_urls.get("Homepage"),
        CANONICAL_SITE_URL,
        "Homepage URL",
    )
    add_equal_check(
        failures,
        "pyproject.toml: [project.urls].Documentation",
        project_urls.get("Documentation"),
        CANONICAL_SITE_URL,
        "Documentation URL",
    )
    add_equal_check(
        failures,
        "package.json: homepage",
        package_json.get("homepage"),
        CANONICAL_SITE_URL,
        "homepage URL",
    )
    add_equal_check(
        failures,
        "package.json: documentation",
        package_json.get("documentation"),
        CANONICAL_SITE_URL,
        "documentation URL",
    )

    add_site_url_checks(
        failures,
        "Makefile",
        r"scripts/check_site\.py\s+--base-url\s+(\S+)",
        "site-health URL",
    )
    add_site_url_checks(
        failures,
        "scripts/check_site.py",
        r'--base-url["\']\s*,\s*default\s*=\s*["\']([^"\']+)["\']',
        "default site-health URL",
    )
    add_site_url_checks(
        failures,
        ".github/workflows/site-health.yml",
        r"scripts/check_site\.py\s+--base-url\s+(\S+)",
        "site-health workflow URL",
    )

    for relative_path in ["README.md", "LICENSE", "docs/en", "docs/zh"]:
        if not (ROOT / relative_path).exists():
            failures.append(f"{relative_path}: required release file is missing")

    if failures:
        for failure in failures:
            print(f"release-check: {failure}", file=sys.stderr)
        raise SystemExit(1)

    print("release-check: ok")


if __name__ == "__main__":
    main()
