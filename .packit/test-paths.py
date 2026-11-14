#!/usr/bin/env python3
"""Check Packit monorepo paths and archive actions without downloading sources."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
config = json.loads(subprocess.check_output(["yq", "-o=json", ".", str(root / ".packit.yaml")]))

for job in config["jobs"]:
    assert job["job"] == "copr_build"
    assert len(job["packages"]) == 1 and job["packages"][0] in config["packages"]
    assert job["identifier"] == job["packages"][0]
    # Pi, REA and Vite+ use networked build inputs; Morphe resolves Maven dependencies.
    if job.get("enable_net", False):
        assert set(job["packages"]) <= {"morphe", "pi-coding-agent", "rea", "vite-plus"}
    if job["trigger"] == "commit":
        assert job["branch"] == "main$"
        assert job["owner"] == "zeldrisho" and job["project"] == "packages"
for package in config["packages"]:
    jobs = [job for job in config["jobs"] if job["packages"] == [package]]
    if jobs:
        assert len(jobs) == 2 and {job["trigger"] for job in jobs} == {"pull_request", "commit"}, package
        assert len({job.get("enable_net", False) for job in jobs}) == 1, package
package_dirs = {path.name for path in (root / "packages").iterdir() if path.is_dir()}
assert package_dirs == set(config["packages"]), f"Unconfigured or missing packages: {package_dirs ^ set(config['packages'])}"
print("Packit jobs are paired and refer to configured packages and documented network exceptions")

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    shutil.copytree(root / ".packit", tmp / ".packit")
    bin_dir = tmp / "bin"
    bin_dir.mkdir()
    for name, body in {
        "spectool": 'touch v1.2.3.tar.gz 1.2.3.tar.gz rea-agents-1.2.3.tgz pi-coding-agent-1.2.3.tgz kotlin-cli-1.2.3-wrapper\n',
        "rpmspec": 'printf 1.2.3\n',
    }.items():
        tool = bin_dir / name
        tool.write_text('#!/bin/sh\n' + body)
        tool.chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}")
    for package, settings in config["packages"].items():
        package_dir = tmp / "packages" / package
        package_dir.mkdir(parents=True)
        spec = settings["specfile_path"]
        assert spec == f"{package}.spec"
        assert (root / "packages" / package / spec).is_file()
        assert f"packages/{package}" in settings["paths"]
        (package_dir / spec).touch()
        result = subprocess.check_output(settings["actions"]["create-archive"].split(), cwd=package_dir, env=env, text=True).strip()
        expected = {
            "kotlin-toolchain": "kotlin-cli-1.2.3-wrapper",
            "rea": "rea-agents-1.2.3.tgz",
            "pi-coding-agent": "pi-coding-agent-1.2.3.tgz",
            "homebrew": "1.2.3.tar.gz",
            "smali": "1.2.3.tar.gz",
        }.get(package, "v1.2.3.tar.gz")
        assert result == expected
        assert (package_dir / result).is_file()
        print(f"{package}: paths and archive action OK")
