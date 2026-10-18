#!/usr/bin/env python3
"""Validate a comma-separated package selection and print one name per line."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def package_names() -> list[str]:
    """Return sorted package directory names that have a matching spec file."""
    packages = ROOT / "packages"
    return sorted(path.name for path in packages.iterdir()
                  if path.is_dir() and (path / f"{path.name}.spec").is_file())


def selected_packages(requested: str, available: list[str]) -> list[str]:
    """Validate and sort a comma-separated explicit package selection."""
    names = {name.strip() for name in requested.split(",") if name.strip()}
    unknown = sorted(names - set(available))
    if not names:
        raise ValueError("at least one package name is required")
    if unknown:
        raise ValueError(f"unknown package(s): {', '.join(unknown)}")
    return sorted(names)


def main() -> int:
    """Print the selected packages and return the exit status."""
    if len(sys.argv) != 2:
        print("usage: select_packages.py NAMES", file=sys.stderr)
        return 2
    try:
        print("\n".join(selected_packages(sys.argv[1], package_names())))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
