#!/usr/bin/env python3
"""Create a source and notice archive for Yazi's approved syntax set.

Run against a checkout of yazi-rs/prebuilt at the commit pinned by Yazi's
published yazi-prebuilt crate, after initializing its supported submodules.
"""

from __future__ import annotations

import argparse
import configparser
import gzip
import io
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

OMITTED = {
    "syntaxes/hosts": "upstream repository is unavailable; no source snapshot",
    "syntaxes/less": "no license grant found for the pinned snapshot",
    "syntaxes/livescript": "upstream repository is unavailable; no source snapshot",
    "syntaxes/nginx": "upstream repository is unavailable; no source snapshot",
    "syntaxes/verilog": "no license grant found for the pinned snapshot",
}
LICENSE_NAMES = {
    "license",
    "licence",
    "copying",
    "copyright",
    "notice",
}


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def modules(repo: Path) -> list[tuple[str, str, str]]:
    config = configparser.ConfigParser()
    config.read_string((repo / ".gitmodules").read_text())
    urls = {
        section.removeprefix('submodule "').removesuffix('"'): values["url"]
        for section, values in config.items()
        if section.startswith("submodule ")
    }
    tree = git(repo, "ls-tree", "-r", "HEAD", "syntaxes")
    result = []
    for line in tree.splitlines():
        mode, kind, commit, path = line.split(maxsplit=3)
        if mode == "160000" and kind == "commit":
            path = path.removeprefix("syntaxes/")
            full_path = f"syntaxes/{path}"
            result.append((full_path, commit, urls[full_path]))
    return sorted(result)


def selected_files(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    files = []
    for member in archive.getmembers():
        if not member.isfile():
            continue
        name = PurePosixPath(member.name).name
        lower = name.lower()
        if lower.endswith(".sublime-syntax") or lower == "readme.md":
            files.append(member)
        elif any(lower.startswith(prefix) for prefix in LICENSE_NAMES):
            files.append(member)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prebuilt", type=Path, help="checkout of yazi-rs/prebuilt")
    parser.add_argument("output", type=Path, help="output syntax-source archive")
    parser.add_argument("--ssh-license", type=Path, required=True, help="upstream GPL license text")
    parser.add_argument("--version", required=True, help="Yazi package version")
    args = parser.parse_args()
    repo = args.prebuilt.resolve()
    commit = git(repo, "rev-parse", "HEAD")
    source_modules = modules(repo)
    included = [path for path, _, _ in source_modules if path not in OMITTED]
    subprocess.run(
        ["git", "-C", str(repo), "submodule", "update", "--init", "--depth=1", "--", *included],
        check=True,
    )
    for path in OMITTED:
        excluded = repo / path
        if excluded.is_symlink() or excluded.is_file():
            excluded.unlink()
        elif excluded.exists():
            shutil.rmtree(excluded)

    output_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=output_buffer, mode="wb", filename="", mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as target:
            readme = [
                f"Yazi v{args.version} syntax source provenance",
                f"Prebuilt repository commit: {commit}",
                "",
                f"Source and license/notice files for the {len(included)} pinned syntax submodules retained in",
                "Yazi's filtered prebuilt syntax database. The package filters the published",
                "SyntaxSet; it does not compile syntax definitions from these sources during RPM",
                "builds.",
                "Syntax definitions excluded from the bundled database:",
            ]
            for path, reason in sorted(OMITTED.items()):
                readme.append(f"- {path}: {reason}")
            readme.extend(["", "Included upstream repositories and pins:"])

            license_texts = []
            for module_path, pinned_commit, url in source_modules:
                if module_path in OMITTED:
                    continue
                module = repo / module_path
                if not module.is_dir() or not (module / ".git").exists():
                    raise SystemExit(f"required syntax submodule is not initialized: {module_path}")
                actual_commit = git(module, "rev-parse", "HEAD")
                if actual_commit != pinned_commit:
                    raise SystemExit(f"{module_path} is at {actual_commit}, expected {pinned_commit}")
                readme.append(f"- {module_path}: {url} ({pinned_commit})")
                source_tar = subprocess.check_output(["git", "-C", str(module), "archive", "--format=tar", pinned_commit])
                with tarfile.open(fileobj=io.BytesIO(source_tar), mode="r:") as source:
                    for member in selected_files(source):
                        rel = PurePosixPath(member.name)
                        data = source.extractfile(member)
                        if data is None:
                            continue
                        content = data.read()
                        if any(rel.name.lower().startswith(prefix) for prefix in LICENSE_NAMES):
                            license_texts.append((f"{module_path}/{rel}", content.decode(errors="replace")))
                        info = tarfile.TarInfo(f"syntax-sources/{module_path}/{rel}")
                        info.size = len(content)
                        info.mode = member.mode & 0o644
                        info.uid = info.gid = 0
                        info.uname = info.gname = ""
                        info.mtime = 0
                        target.addfile(info, io.BytesIO(content))

            aggregate = ["Yazi syntax-source license notices", ""]
            for path, text in license_texts:
                aggregate.extend([f"===== {path} =====", text.rstrip(), ""])

            for name, content in (
                ("syntax-sources/README.md", "\n".join(readme) + "\n"),
                ("syntax-sources/LICENSE.syntaxes", "\n".join(aggregate)),
                ("syntax-sources/LICENSE.ssh-config", args.ssh_license.read_text()),
            ):
                encoded = content.encode()
                info = tarfile.TarInfo(name)
                info.size = len(encoded)
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                info.mtime = 0
                target.addfile(info, io.BytesIO(encoded))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output_buffer.getvalue())
    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
