#!/usr/bin/env python3
"""Replace the vendored Yazi syntax database and refresh Cargo's file checksum."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile


VENDOR_MEMBER = "vendor/yazi-prebuilt/built/syntaxes"
CHECKSUM_MEMBER = "vendor/yazi-prebuilt/.cargo-checksum.json"


def safe_extract(archive_path: Path, destination: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "vendor":
                raise SystemExit(f"unsafe or unexpected vendor archive path: {member.name}")
            target = destination.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise SystemExit(f"cannot read archive member: {member.name}")
                target.write_bytes(source.read())
                target.chmod(member.mode & 0o777)
            elif member.issym():
                raise SystemExit(f"unexpected symlink in vendor archive: {member.name}")
            else:
                raise SystemExit(f"unsupported vendor archive member type: {member.name}")


def write_archive(root: Path, output: Path) -> None:
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                top = tarfile.TarInfo("vendor/")
                top.type = tarfile.DIRTYPE
                top.mode = 0o755
                top.uid = top.gid = 0
                top.uname = top.gname = ""
                top.mtime = 0
                archive.addfile(top)
                for path in sorted(root.rglob("*")):
                    info = archive.gettarinfo(str(path), arcname=path.relative_to(root.parent).as_posix())
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    if path.is_file() and not path.is_symlink():
                        with path.open("rb") as source:
                            archive.addfile(info, source)
                    else:
                        archive.addfile(info)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vendor_archive", type=Path, help="current cargo vendor tarball")
    parser.add_argument("generated_syntaxes", type=Path, help="filtered built/syntaxes output")
    parser.add_argument("output", type=Path, help="destination vendor tarball")
    args = parser.parse_args()
    if not args.generated_syntaxes.is_file():
        raise SystemExit(f"syntax database not found: {args.generated_syntaxes}")

    with tempfile.TemporaryDirectory(prefix="yazi-vendor-") as temporary:
        root = Path(temporary)
        safe_extract(args.vendor_archive, root)
        syntax_path = root / VENDOR_MEMBER
        checksum_path = root / CHECKSUM_MEMBER
        if not syntax_path.is_file() or not checksum_path.is_file():
            raise SystemExit("vendor archive is missing yazi-prebuilt syntax data or checksum metadata")
        shutil.copyfile(args.generated_syntaxes, syntax_path)
        checksum = json.loads(checksum_path.read_text())
        checksum["files"]["built/syntaxes"] = hashlib.sha256(syntax_path.read_bytes()).hexdigest()
        checksum_path.write_text(json.dumps(checksum, separators=(",", ":")) + "\n")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_archive(root / "vendor", args.output)

    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")
    print(f"Filtered syntax SHA256: {hashlib.sha256(args.generated_syntaxes.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
