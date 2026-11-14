#!/usr/bin/env python3
"""Reject staged package updates that touch other packages or the wrong version."""
import pathlib
import re
import subprocess
import sys


def check(package, version, changed, spec, proposal):
    prefix = f"packages/{package}/"
    if not changed:
        raise ValueError("Update changed no files")
    outside = [path for path in changed if not path.startswith(prefix)]
    if outside:
        raise ValueError(f"Update changed files outside {prefix}: {', '.join(outside)}")
    if proposal:
        return "manual proposal; packaged version not checked"
    versions = re.findall(r"^Version:\s*(\S+)\s*$", spec, re.MULTILINE | re.IGNORECASE)
    if versions != [version]:
        raise ValueError(f"Spec Version must be exactly {version}")
    return f"{package}: staged changes match version {version}"


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: verify-update.py PACKAGE VERSION")
    package, version = sys.argv[1:]
    if not re.fullmatch(r"[A-Za-z0-9_+.-]+", package) or package in {".", ".."}:
        sys.exit("Invalid package name")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
        sys.exit("Invalid version")
    package_dir = pathlib.Path("packages") / package
    changed = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], text=True
    ).splitlines()
    spec = package_dir / f"{package}.spec"
    print(check(
        package=package,
        version=version,
        changed=changed,
        spec=spec.read_text() if spec.is_file() else "",
        proposal=(package_dir / "livecheck-update.txt").is_file(),
    ))


if __name__ == "__main__":
    main()
