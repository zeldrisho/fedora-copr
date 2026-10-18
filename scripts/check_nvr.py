#!/usr/bin/env python3
"""Require a newer RPM EVR when build-relevant package inputs change."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_PATH = re.compile(r"^packages/([^/]+)/")
IGNORED = re.compile(r"^packages/[^/]+/(?:README\.md|docs/)")
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

    The current spec must contain the exact changelog marker documenting that
    prior COPR builds were withdrawn and confirmed not downloaded or installed,
    and the previous spec must not: the marker authorizes one reset, not every
    later change that leaves Release at 1.
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
        and INITIAL_RELEASE_RESET_MARKER not in previous
    )


SECTION = re.compile(
    r"^%(description|package|prep|conf|generate_buildrequires|build|install|check|files|"
    r"changelog|pre|post|preun|postun|pretrans|posttrans|preuntrans|postuntrans|"
    r"verifyscript|trigger\w*|filetrigger\w*|transfiletrigger\w*|sepolicy)\b"
)
PACKAGER_ONLY_SECTIONS = {"check", "changelog"}


def user_facing_spec(text: str, *, ignore_packager_buildrequires: bool = True) -> str:
    """Return the spec text that can change what users get.

    Drop full-line comments, blank lines, and the %check and %changelog
    sections, since edits confined to those do not alter the installed package.
    """
    kept: list[str] = []
    skipping = False
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = SECTION.match(line)
        if match:
            skipping = match.group(1) in PACKAGER_ONLY_SECTIONS
        if skipping or not line.strip() or line.lstrip().startswith("#"):
            continue
        if (ignore_packager_buildrequires and index
                and lines[index - 1].strip() == "# packager-only: BuildRequires"
                and re.match(r"^BuildRequires:", line)):
            continue
        kept.append(line.rstrip())
    return "\n".join(kept)


def is_remote_source_cache(path: str, spec: str) -> bool:
    """Return whether a package file duplicates a remotely fetched Source URL.

    This permits removing a checked-in cache of an upstream archive when the
    spec still declares that exact archive as a remote source for SRPM creation.
    Modified or newly added source archives remain build-input changes.
    """
    name_match = re.search(r"^Name:\s*(\S+)", spec, re.MULTILINE)
    try:
        version, _ = spec_values(spec)
    except ValueError:
        return False
    if not name_match:
        return False
    filename = path.rsplit("/", 1)[-1]
    sources = [
        source.replace("%{name}", name_match.group(1)).replace("%{version}", version)
        for source in re.findall(r"^Source\d*:\s*(\S+)", spec, re.MULTILINE)
    ]
    local_sources = {
        unquote(source.rsplit("/", 1)[-1])
        for source in sources
        if not urlsplit(source).scheme
    }
    if filename in local_sources:
        return False
    for source in sources:
        parsed = urlsplit(source)
        if not parsed.scheme:
            continue
        selected_path = parsed.fragment if parsed.fragment.startswith("/") else parsed.path
        if unquote(selected_path.rsplit("/", 1)[-1]) == filename:
            return True
    return False


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
    each package's top-level README.md and files under its docs/ directory. Skip
    packages whose spec is absent or empty at either revision, and spec-only
    changes confined to comments, %check, and %changelog. Print results and return 0 on success, including
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
    deleted_paths = set(git(
        "diff", "--diff-filter=D", "--name-only", mergebase, "HEAD", "--", "packages/"
    ).splitlines())
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
        files = [item for item in changed if item.startswith(f"packages/{name}/")]
        files = [item for item in files if not (
            item in deleted_paths and is_remote_source_cache(item, previous)
        )]
        if not files:
            print(f"{name}: removed cached remote source; no bump required")
            continue
        if files == [path] and (
            user_facing_spec(current, ignore_packager_buildrequires=False)
            == user_facing_spec(previous, ignore_packager_buildrequires=False)
            or user_facing_spec(current) == user_facing_spec(previous)
        ):
            print(f"{name}: packager-only spec change; no bump required")
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
