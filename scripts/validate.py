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
TOOLS = ("rpmspec", "rpmbuild", "spectool", "rpmlint", "make")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str], *, cwd: Path | None = None, capture: bool = False) -> str:
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


def main() -> None:
    for tool in TOOLS:
        if shutil.which(tool) is None:
            fail(f"required tool is missing: {tool}")
    if not PACKAGES.is_dir():
        fail(f"packages directory not found: {PACKAGES}")

    package_dirs = sorted(path for path in PACKAGES.iterdir() if path.is_dir())
    if not package_dirs:
        print("No packages found; validation passed.")
        return

    validated = 0
    for package_dir in package_dirs:
        name = package_dir.name
        spec = package_dir / f"{name}.spec"
        if not spec.is_file():
            fail(f"expected spec not found: packages/{name}/{name}.spec")

        print(f"Validating {name}...", flush=True)
        output = run(
            ["rpmspec", "-q", "--qf", "%{name}\\n", str(spec)], capture=True
        )
        names = [line.strip() for line in output.splitlines() if line.strip()]
        if not names or names[0] != name:
            actual = names[0] if names else "(no Name found)"
            fail(f"package directory/spec name is {name!r} but Name: is {actual!r}")

        run(["rpmspec", "-P", str(spec)], capture=True)
        with tempfile.TemporaryDirectory(prefix=f"fedora-copr-{name}-") as temporary:
            outdir = Path(temporary) / "srpms"
            run(
                [
                    "make",
                    "-f",
                    str(MAKEFILE),
                    "srpm",
                    f"spec={name}.spec",
                    f"outdir={outdir}",
                ],
                cwd=package_dir,
            )
            srpms = sorted(outdir.glob("*.src.rpm"))
            if not srpms:
                fail(f"SRPM target produced no source RPM for {name}")
            run(["rpmlint", str(spec), *(str(srpm) for srpm in srpms)])
        validated += 1

    print(f"Validated {validated} package(s).")


if __name__ == "__main__":
    main()
