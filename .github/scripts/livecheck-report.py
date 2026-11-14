#!/usr/bin/env python3
"""Compare selected files in old and new Source0 archives without extracting them."""
import hashlib
import importlib.util
import io
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

spec = importlib.util.spec_from_file_location("livecheck", Path(__file__).with_name("livecheck.py"))
livecheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(livecheck)

MAX_ARCHIVE = 100 * 1024 * 1024
MAX_FILE = 10 * 1024 * 1024
MAX_MEMBERS = 100000
NAMES = {"package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml",
         "cargo.toml", "cargo.lock", "go.mod", "go.sum", "gemfile", "gemfile.lock",
         "pyproject.toml", "requirements.txt", "poetry.lock", "uv.lock", "composer.json", "composer.lock",
         "build.gradle", "build.gradle.kts", "pom.xml", "gradle.properties", "makefile", "cmakelists.txt",
         "meson.build", "configure", "configure.ac", "rust-toolchain", "rust-toolchain.toml", ".nvmrc"}


def relevant(path):
    name = PurePosixPath(path).name.lower()
    return name in NAMES or name.startswith(("license", "licence", "copying", "notice"))


def archive_files(data):
    """Hash relevant regular files; never extract archive paths or follow links."""
    result = {}
    stream = io.BytesIO(data)
    if zipfile.is_zipfile(stream):
        with zipfile.ZipFile(stream) as archive:
            members = archive.infolist()
            if len(members) > MAX_MEMBERS:
                raise ValueError("too many archive members")
            for member in members:
                if member.is_dir() or not relevant(member.filename):
                    continue
                if member.file_size > MAX_FILE:
                    raise ValueError("selected file too large")
                add_file(result, member.filename, archive.read(member))
    else:
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r:*") as archive:
            for count, member in enumerate(archive, 1):
                if count > MAX_MEMBERS:
                    raise ValueError("too many archive members")
                if not member.isfile() or not relevant(member.name):
                    continue
                if member.size > MAX_FILE:
                    raise ValueError("selected file too large")
                with archive.extractfile(member) as source:
                    add_file(result, member.name, source.read(MAX_FILE + 1))
    return result


def add_file(result, path, data):
    parts = PurePosixPath(path).parts
    if len(parts) < 2 or any(part in ("..", ".") for part in parts) or path.startswith("/"):
        raise ValueError("unsupported archive path")
    # Release archives normally have a versioned top-level directory.
    name = "/".join(parts[1:])
    if name in result:
        raise ValueError("duplicate archive path")
    result[name] = hashlib.sha256(data).hexdigest()


def download(url):
    with urllib.request.urlopen(url.split("#", 1)[0], timeout=60) as response:
        data = response.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE:
        raise ValueError("archive exceeds download limit")
    return data


def report(old, new):
    changes = [(path, "added" if path not in old else "removed" if path not in new else "changed")
               for path in sorted(old.keys() | new.keys()) if old.get(path) != new.get(path)]
    lines = ["### Automated source impact report", "",
             "Comparison covers selected dependency manifests, build files and license/notice files in Source0 only."]
    if changes:
        # Code formatting also prevents filenames becoming links or Markdown headings.
        for path, status in changes[:200]:
            safe = path.replace("`", "'").replace("\n", " ").replace("\r", " ")
            lines.append(f"- {status}: `{safe}`")
        if len(changes) > 200:
            lines.append(f"- {len(changes) - 200} additional changes omitted.")
    else:
        lines.append("- No selected file changes detected; this is not a complete source review.")
    return "\n".join(lines)


def main(package):
    if not __import__("re").fullmatch(r"[A-Za-z0-9_+.-]+", package) or package in (".", ".."):
        raise ValueError("invalid package name")
    path = Path("packages") / package / f"{package}.spec"
    old_spec = subprocess.check_output(["git", "show", f"HEAD:{path}"], text=True)
    new_spec = path.read_text()
    name = livecheck.field(new_spec, "Name")
    old_url = livecheck.expand(livecheck.field(old_spec, "Source0"), livecheck.field(old_spec, "Name"), livecheck.field(old_spec, "Version"))
    new_url = livecheck.expand(livecheck.field(new_spec, "Source0"), name, livecheck.field(new_spec, "Version"))
    print(report(archive_files(download(old_url)), archive_files(download(new_url))))


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as error:
        print("### Automated source impact report\n\nComparison unavailable; review sources manually.")
        print(f"Impact report failed: {error}", file=sys.stderr)
