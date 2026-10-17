#!/usr/bin/env python3
"""Build changed package SRPMs in a selected Mock chroot and lint the RPMs."""

from __future__ import annotations

import argparse
import grp
import os
import pwd
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOCK_GROUP = "mock"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    """Run a command, raising SystemExit with its exit status on failure."""
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except FileNotFoundError as exc:
        print(f"error: required command not found: {command[0]}", file=sys.stderr)
        raise SystemExit(127) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc


def changed_packages(base: str | None) -> list[str]:
    """Return build-relevant packages selected by the repository helper."""
    command = [sys.executable, str(ROOT / "scripts/changed_packages.py"), "--build"]
    if base:
        command.append(base)
    result = subprocess.run(
        command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return [line for line in result.stdout.splitlines() if line]


def builder_identity(mock_gid: int) -> tuple[str, int]:
    """Return an unprivileged identity with Mock as its primary group."""
    uid = ROOT.stat().st_uid or 1000
    try:
        account = pwd.getpwuid(uid)
    except KeyError:
        username = f"ci-builder-{uid}"
        run(["useradd", "--uid", str(uid), "--gid", str(mock_gid),
             "--no-create-home", "--shell", "/sbin/nologin", username])
        account = pwd.getpwuid(uid)
    return account.pw_name, uid


def build_package(package: str, chroot: str, workdir: Path,
                  builder: str, builder_uid: int, mock_gid: int,
                  srpm_dir: Path | None = None) -> None:
    """Prepare an SRPM, build it in Mock, and inspect resulting binary RPMs."""
    print(f"Building {package} for {chroot}", flush=True)
    package_dir = ROOT / "packages" / package
    result_dir = workdir / package / "results"
    result_dir.mkdir(parents=True)

    if srpm_dir is None:
        srpm_dir = workdir / package / "srpm"
        srpm_dir.mkdir(parents=True)
        run(["make", "-f", "../../.copr/Makefile", "srpm",
             f"spec={package}.spec", f"outdir={srpm_dir}"], cwd=package_dir)
    else:
        srpm_dir = srpm_dir / package
    srpms = sorted(srpm_dir.glob("*.src.rpm"))
    if len(srpms) != 1:
        raise SystemExit(f"expected one SRPM for {package}, found {len(srpms)}")

    for path in (srpm_dir, result_dir):
        run(["chown", "-R", f"{builder_uid}:{mock_gid}", str(path)])
    run(["runuser", "-u", builder, "-g", MOCK_GROUP, "--", "mock", "-r", chroot,
         "--rebuild", str(srpms[0]), "--resultdir", str(result_dir), "--no-clean"])

    rpms = sorted(path for path in result_dir.glob("*.rpm")
                  if not path.name.endswith(".src.rpm"))
    if not rpms:
        raise SystemExit(f"Mock produced no binary RPMs for {package}")
    run(["rpmlint", *(str(path) for path in rpms)])

    if package == "actionlint":
        rpm = next((path for path in rpms if path.name.startswith("actionlint-")), None)
        if rpm is None:
            raise SystemExit("Mock did not produce the actionlint RPM")
        run(["rpm", "-qp", "--licensefiles", str(rpm)])
        result = subprocess.run(["rpm", "-qp", "--provides", str(rpm)],
                                text=True, stdout=subprocess.PIPE, check=True)
        if "bundled(golang(" not in result.stdout:
            raise SystemExit("actionlint RPM is missing its bundled(golang(...)) provide")
        run(["rpm", "-qp", "--scripts", str(rpm)])
        if chroot == "fedora-44-x86_64":
            run(["dnf", "-y", "install", str(rpm)])
            run(["actionlint", "--version"])
            smoke_file = workdir / "actionlint-smoke.yml"
            smoke_file.write_text(
                "name: CI smoke test\non:\n  push:\njobs:\n"
                "  check:\n    runs-on: ubuntu-latest\n    steps:\n"
                "      - run: echo hello\n",
                encoding="utf-8",
            )
            run(["actionlint", str(smoke_file)])
    elif package == "yazi":
        rpm = next((path for path in rpms if path.name.startswith("yazi-")), None)
        if rpm is None:
            raise SystemExit("Mock did not produce the yazi RPM")
        run(["rpm", "-qp", "--licensefiles", str(rpm)])
        result = subprocess.run(["rpm", "-qp", "--requires", str(rpm)],
                                text=True, stdout=subprocess.PIPE, check=True)
        for requirement in ("liblua-5.4.so", "libonig.so.5"):
            if requirement not in result.stdout:
                raise SystemExit(f"yazi RPM is missing requirement {requirement}")
        if chroot == "fedora-44-x86_64":
            run(["dnf", "-y", "install", str(rpm)])
            run(["yazi", "--version"])
            run(["ya", "--version"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chroot", help="Mock chroot configuration, e.g. fedora-44-x86_64")
    parser.add_argument("--base-ref", help="base commit used to select changed package inputs")
    parser.add_argument("--srpm-dir", type=Path,
                        help="use previously validated SRPMs from this directory")
    parser.add_argument("--workdir", type=Path,
                        help="retain Mock result files under this directory")
    args = parser.parse_args()

    config = Path("/etc/mock") / f"{args.chroot}.cfg"
    if not config.is_file():
        parser.error(f"Mock configuration not installed: {config}")
    if os.geteuid() != 0:
        parser.error("must run as root in the Fedora tooling container")

    packages = changed_packages(args.base_ref)
    if not packages:
        print("No package build inputs changed; no binary RPMs to build.")
        return 0

    mock_gid = grp.getgrnam(MOCK_GROUP).gr_gid
    builder, builder_uid = builder_identity(mock_gid)
    # Mock downloads sources/dependencies while preparing the SRPM/buildroot,
    # but must not expose the network to rpmbuild itself.
    site_defaults = Path("/etc/mock/site-defaults.cfg")
    with site_defaults.open("a", encoding="utf-8") as config_file:
        config_file.write("\nconfig_opts['rpmbuild_networking'] = False\n")

    def run_builds(workdir: Path) -> None:
        workdir.mkdir(parents=True, exist_ok=True)
        workdir.chmod(0o755)
        for package in packages:
            build_package(package, args.chroot, workdir, builder, builder_uid, mock_gid,
                          args.srpm_dir)

    if args.workdir is not None:
        run_builds(args.workdir)
    else:
        with tempfile.TemporaryDirectory(prefix=f"fedora-copr-{args.chroot}-") as temporary:
            run_builds(Path(temporary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
