#!/usr/bin/env python3
"""Print packages affected by a commit range, one name per line."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOBAL_PATHS = (".copr/", ".github/", "scripts/", "tests/", "Makefile")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def package_names() -> list[str]:
    packages = ROOT / "packages"
    return sorted(path.name for path in packages.iterdir()
                  if path.is_dir() and (path / f"{path.name}.spec").is_file())


def changed_packages(base: str | None) -> list[str]:
    available = package_names()
    if base is None or set(base) == {"0"}:
        return available
    files = git("diff", "--name-only", base, "HEAD").splitlines()
    if any(path.startswith(GLOBAL_PATHS) for path in files):
        return available
    changed: set[str] = set()
    for path in files:
        parts = Path(path).parts
        if len(parts) >= 3 and parts[0] == "packages":
            name = parts[1]
            # Package notes do not alter the RPM. Other package-local files do.
            if len(parts) == 3 and parts[2] == "README.md":
                continue
            if name in available:
                changed.add(name)
    return sorted(changed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", help="base commit; omit to select all packages")
    args = parser.parse_args()
    try:
        print("\n".join(changed_packages(args.base)))
    except (RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
