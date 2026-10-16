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
INITIAL_RELEASE_RESET_MARKER = (
    "Initial release reset: all prior COPR builds withdrawn and confirmed "
    "not downloaded or installed"
)
def git(*args: str, check: bool = True) -> str:
    """Run Git in the repository root and return its standard output.

    Raise RuntimeError on a nonzero exit unless check is False, in which case
    return the output even on failure. Process startup errors propagate.
    """
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def spec_values(text: str) -> tuple[str, str]:
    """Return the first tokens of the spec's Version and Release fields.

    Require exactly one match for each case-sensitive field at a line's start;
    otherwise raise ValueError. RPM macros are returned without expansion.
    """
    values: dict[str, str] = {}
    for key in ("Version", "Release"):
        matches = re.findall(rf"^{key}:\s*(\S+)", text, re.MULTILINE)
        if len(matches) != 1:
            raise ValueError(f"expected one literal {key}: field, found {len(matches)}")
        values[key] = matches[0]
    return values["Version"], values["Release"]


def is_authorized_initial_release_reset(current: str, previous: str) -> bool:
    """Allow a verified initial-release reset to Release 1 for the same Version.

    The current spec must retain the exact changelog marker documenting that
    prior COPR builds were withdrawn and confirmed not downloaded or installed.
    """
    try:
        current_version, current_release = spec_values(current)
        previous_version, _ = spec_values(previous)
    except ValueError:
        return False
    return (
        current_version == previous_version
        and current_release in {"1", "1%{?dist}"}
        and INITIAL_RELEASE_RESET_MARKER in current
    )


def rpmvercmp(left: str, right: str) -> int:
    """Compare version-release strings using RPM's ordering.

    Return a negative integer, zero, or a positive integer when left is less
    than, equal to, or greater than right. CalledProcessError propagates if RPM
    fails, OSError if it cannot start, and ValueError if its output is not an
    integer.
    """
    # Escape Lua string contents before asking RPM to compare EVRs.
    def lua_string(value: str) -> str:
        """Quote a Lua string, escaping backslashes and double quotes."""
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

    expression = f"%{{lua: print(rpm.vercmp({lua_string(left)}, {lua_string(right)}))}}"
    result = subprocess.run(["rpm", "--eval", expression], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return int(result.stdout.strip())


def check(base: str) -> int:
    """Require version-release increases for packages changed since base.

    Compare committed HEAD with its merge base with the Git ref base, ignoring
    each package's top-level README.md. Skip packages whose spec is absent or
    empty at either revision. Print results and return 0 on success, including
    when no packages need comparison, or 1 for invalid fields, RPM subprocess
    failure, or a version-release that did not increase.

    Git RuntimeError and process startup OSError exceptions propagate.
    """
    mergebase = git("merge-base", base, "HEAD").strip()
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
        if comparison <= 0 and is_authorized_initial_release_reset(current, previous):
            print(f"{name}: authorized initial-release reset to {new_evr}")
        elif comparison <= 0:
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
    """Parse the base ref from the command line and return the check status.

    Report Git RuntimeError failures and return 1; process startup OSError
    exceptions propagate. Argument parsing may raise SystemExit.
    """
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
