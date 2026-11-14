#!/usr/bin/env python3
"""Reject staged package updates that touch other packages or the wrong version."""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


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
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: verify-update.py PACKAGE VERSION [PATCH]")
    package, version = sys.argv[1:3]
    if not re.fullmatch(r"[A-Za-z0-9_+.-]+", package) or package in {".", ".."}:
        sys.exit("Invalid package name")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
        sys.exit("Invalid version")
    def verify(env):
        changed = subprocess.check_output(
            ["git", "diff", "--cached", "--no-renames", "--name-only", "-z"], env=env
        ).decode("utf-8", "surrogateescape").split("\0")[:-1]
        # Symlinks must not redirect the spec or proposal marker outside the package.
        entries = subprocess.check_output(["git", "ls-files", "--stage", "-z"], env=env)
        for entry in entries.split(b"\0"):
            if entry and entry.split(b" ", 1)[0] == b"120000":
                path = entry.split(b"\t", 1)[1].decode("utf-8", "surrogateescape")
                if path in changed:
                    raise ValueError(f"Update adds or changes a symlink: {path}")
        package_dir = pathlib.PurePosixPath("packages") / package
        def staged(path):
            result = subprocess.run(["git", "show", f":{path}"], env=env, capture_output=True)
            return result.stdout.decode("utf-8") if result.returncode == 0 else None
        spec = staged(package_dir / f"{package}.spec")
        proposal = staged(package_dir / "livecheck-update.txt")
        print(check(package, version, changed, spec or "", proposal is not None))

    if len(sys.argv) == 4:
        # Apply untrusted input only to a disposable index, never to the working tree.
        with tempfile.TemporaryDirectory() as tmp:
            index = os.path.join(tmp, "index")
            current = subprocess.check_output(["git", "rev-parse", "--git-path", "index"], text=True).strip()
            shutil.copyfile(current, index)
            env = dict(os.environ, GIT_INDEX_FILE=index)
            subprocess.run(["git", "apply", "--cached", "--", sys.argv[3]], env=env, check=True)
            verify(env)
    else:
        verify(os.environ.copy())


if __name__ == "__main__":
    main()
