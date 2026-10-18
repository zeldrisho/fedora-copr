#!/usr/bin/env python3
"""Print packages affected by a commit range, one name per line."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLOBAL_PATHS = (".copr/", ".github/", "scripts/", "tests/", "Makefile")
# Shared SRPM preparation changes can alter every package's built contents.
PUBLISH_GLOBAL_PATHS = (".copr/",)


def git(*args: str) -> str:
    """Run Git in the repository root, returning stdout or raising RuntimeError."""
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def package_names() -> list[str]:
    """Return sorted package directory names that have a matching spec file."""
    packages = ROOT / "packages"
    return sorted(path.name for path in packages.iterdir()
                  if path.is_dir() and (path / f"{path.name}.spec").is_file())


def changed_packages(base: str | None, global_paths: tuple[str, ...] = GLOBAL_PATHS) -> list[str]:
    """Select packages changed from base to HEAD, ignoring README and docs files.

    Select all packages when base is absent or all zeros, or when a changed
    path starts with one of the supplied shared-input prefixes in global_paths.
    """
    available = package_names()
    if base is None or set(base) == {"0"}:
        return available
    files = git("diff", "--name-only", base, "HEAD").splitlines()
    if any(path.startswith(global_paths) for path in files):
        return available
    changed: set[str] = set()
    for path in files:
        parts = Path(path).parts
        if len(parts) >= 3 and parts[0] == "packages":
            name = parts[1]
            # Package documentation does not alter the RPM. Other local files do.
            if (len(parts) == 3 and parts[2] == "README.md") or parts[2] == "docs":
                continue
            if name in available:
                changed.add(name)
    return sorted(changed)


def main() -> int:
    """Print packages selected for validation or publishing and return the status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", help="base commit; omit to select all packages")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--publish", action="store_true",
        help="select packages for COPR submission: only .copr/ changes count as shared",
    )
    args = parser.parse_args()
    try:
        if args.publish:
            paths = PUBLISH_GLOBAL_PATHS
        else:
            paths = GLOBAL_PATHS
        print("\n".join(changed_packages(args.base, paths)))
    except (RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
