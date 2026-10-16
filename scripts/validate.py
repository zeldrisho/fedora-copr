#!/usr/bin/env python3
"""Validate package specs and build/lint source RPMs through the COPR Makefile."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
MAKEFILE = ROOT / ".copr" / "Makefile"
RPMLINTRC = ROOT / "scripts" / "rpmlintrc"
TOOLS = ("rpmspec", "rpmbuild", "spectool", "rpmlint", "make")


def fail(message: str) -> None:
    """Print an error to standard error and raise SystemExit with status 1."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str], *, cwd: Path | None = None, capture: bool = False) -> str:
    """Run a command in cwd, inheriting the working directory when it is None.

    With capture=True, return standard output on success and forward both
    captured streams to standard error on failure. Otherwise inherit the output
    streams and return an empty string. A nonzero exit raises SystemExit with
    the command's status; process startup OSError exceptions propagate.
    """
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode:
        if capture:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout if capture else ""


def validate_package(package_dir: Path, temporary: Path) -> None:
    """Check a package's spec, build one SRPM, and lint both in a scratch copy.

    Expect a spec named after package_dir whose queried Name matches the directory
    name. Create package and srpms subdirectories under temporary; both must not
    already exist. Leave the copied sources and build artifacts there for the
    caller to clean up.

    Raise SystemExit(1) for a name mismatch or an SRPM count other than one, or
    SystemExit with a failed command's status. File and process startup errors
    propagate.
    """
    name = package_dir.name
    spec_name = f"{name}.spec"
    temporary.mkdir(parents=True, exist_ok=True)
    work_dir = temporary / "package"
    shutil.copytree(package_dir, work_dir)
    spec = work_dir / spec_name

    print(f"Validating {name}...", flush=True)
    output = run(["rpmspec", "-q", "--qf", "%{name}\\n", str(spec)], capture=True)
    names = [line.strip() for line in output.splitlines() if line.strip()]
    if not names or names[0] != name:
        actual = names[0] if names else "(no Name found)"
        fail(f"package directory/spec name is {name!r} but Name: is {actual!r}")

    run(["rpmspec", "-P", str(spec)], capture=True)
    outdir = temporary / "srpms"
    outdir.mkdir()
    run(
        ["make", "-f", str(MAKEFILE), "srpm", f"spec={spec_name}", f"outdir={outdir}"],
        cwd=work_dir,
    )
    srpms = sorted(outdir.glob("*.src.rpm"))
    if len(srpms) != 1:
        fail(f"expected exactly one SRPM for {name}, found {len(srpms)}")
    run(["rpmlint", "--rpmlintrc", str(RPMLINTRC), str(spec), str(srpms[0])])


def main() -> None:
    """Validate every package using temporary directories cleaned up afterward.

    Require all validation tools and the packages directory even when it is
    empty. Raise SystemExit(1) for missing tools, directories, or expected specs;
    package validation errors propagate. Print a summary on success, including
    when no package directories exist.
    """
    for tool in TOOLS:
        if shutil.which(tool) is None:
            fail(f"required tool is missing: {tool}")
    if not PACKAGES.is_dir():
        fail(f"packages directory not found: {PACKAGES}")

    package_dirs = sorted(path for path in PACKAGES.iterdir() if path.is_dir())
    if not package_dirs:
        print("No packages found; validation passed.")
        return

    for package_dir in package_dirs:
        if not (package_dir / f"{package_dir.name}.spec").is_file():
            fail(f"expected spec not found: packages/{package_dir.name}/{package_dir.name}.spec")
        with tempfile.TemporaryDirectory(prefix=f"fedora-copr-{package_dir.name}-") as temporary:
            validate_package(package_dir, Path(temporary))

    print(f"Validated {len(package_dirs)} package(s).")


if __name__ == "__main__":
    main()
