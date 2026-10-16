#!/usr/bin/env python3
"""Require a newer RPM EVR when build-relevant package inputs change."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_PATH = re.compile(r"^packages/([^/]+)/")
IGNORED = re.compile(r"^packages/[^/]+/README\.md$")


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def spec_values(text: str) -> tuple[str, str]:
    values: dict[str, str] = {}
    for key in ("Version", "Release"):
        matches = re.findall(rf"^{key}:\s*(\S+)", text, re.MULTILINE)
        if len(matches) != 1:
            raise ValueError(f"expected one literal {key}: field, found {len(matches)}")
        values[key] = matches[0]
    return values["Version"], values["Release"]


def rpmvercmp(left: str, right: str) -> int:
    # Escape Lua string contents before asking RPM to compare EVRs.
    def lua_string(value: str) -> str:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

    expression = f"%{{lua: print(rpm.vercmp({lua_string(left)}, {lua_string(right)}))}}"
    result = subprocess.run(["rpm", "--eval", expression], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return int(result.stdout.strip())


def check(base: str) -> int:
    mergebase = git("merge-base", base, "HEAD", check=False).strip()
    if not mergebase:
        print(f"error: cannot find a merge base with {base}; fetch more history", file=sys.stderr)
        return 1

    changed = [line for line in git("diff", "--name-only", mergebase, "HEAD", "--", "packages/").splitlines()
               if not IGNORED.match(line)]
    packages = sorted({match.group(1) for path in changed if (match := PACKAGE_PATH.match(path))})
    status = 0
    for name in packages:
        path = f"packages/{name}/{name}.spec"
        current = git("show", f"HEAD:{path}", check=False)
        previous = git("show", f"{mergebase}:{path}", check=False)
        if not current:
            print(f"{name}: package removed; no bump required")
            continue
        if not previous:
            print(f"{name}: new package")
            continue
        try:
            old_evr = "-".join(spec_values(previous))
            new_evr = "-".join(spec_values(current))
            comparison = rpmvercmp(new_evr, old_evr)
        except (ValueError, subprocess.SubprocessError) as exc:
            print(f"error: {name}: cannot compare package EVR: {exc}", file=sys.stderr)
            return 1
        if comparison <= 0:
            files = [item for item in changed if item.startswith(f"packages/{name}/")]
            print(f"{name}: build inputs changed but EVR did not increase ({old_evr} -> {new_evr}):")
            for item in files:
                print(f"    {item}")
            print(f'    Bump Version or Release and add a %changelog entry.')
            status = 1
        else:
            print(f"{name}: EVR increased ({old_evr} -> {new_evr})")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", help="base branch/ref to compare against")
    args = parser.parse_args()
    try:
        return check(args.base)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
