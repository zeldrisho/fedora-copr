#!/usr/bin/env python3
"""Open one issue per package when GitHub reports a newer stable release."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPOSITORIES = {"actionlint": "rhysd/actionlint", "herdr": "herdrdev/herdr", "yazi": "sxyazi/yazi"}


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"command failed: {' '.join(args)}")
    return result.stdout.strip()


def version_key(value: str) -> tuple[tuple[int, object], ...]:
    """Compare simple numeric/dotted upstream tags, ignoring a leading v."""
    value = value.removeprefix("v")
    parts = re.findall(r"\d+|[A-Za-z]+", value)
    if not parts:
        raise ValueError(f"unsupported version: {value!r}")
    return tuple((0, int(part)) if part.isdigit() else (1, part.lower()) for part in parts)


def package_version(package: str) -> str:
    spec = ROOT / "packages" / package / f"{package}.spec"
    match = re.search(r"^Version:\s*(\S+)", spec.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise ValueError(f"Version: not found in {spec}")
    return match.group(1)


def main() -> int:
    repository = os.environ["GH_REPO"]
    for package, upstream in REPOSITORIES.items():
        current = package_version(package)
        latest = run("gh", "api", f"repos/{upstream}/releases/latest", "--jq", ".tag_name")
        if version_key(latest) <= version_key(current):
            print(f"{package}: current {current}, latest stable {latest}")
            continue
        title = f"feat({package}): update to {latest}"
        existing = run("gh", "issue", "list", "--repo", repository, "--state", "open", "--search", title, "--json", "title", "--jq", ".[].title")
        if title in existing.splitlines():
            print(f"{package}: issue already open for {latest}")
            continue
        body = (f"The scheduled upstream check found **{latest}**, while this repository packages **{current}**.\n\n"
                "Review the upstream release, sources, licensing, and Fedora packaging requirements before updating. "
                "This report does not establish that the newer release is suitable or automatically update the package.")
        run("gh", "issue", "create", "--repo", repository, "--title", title, "--body", body)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
