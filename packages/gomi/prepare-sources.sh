#!/usr/bin/env bash
# Run in COPR's SRPM builder after spectool downloads Source0.
set -euo pipefail
spec=$1
sources=$2
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
archive="$sources/v${version}.tar.gz"

printf '%s  %s\n' "$(<source.sha256)" "$archive" | sha256sum -c -
if [ "${SOURCES_DEPS_PREINSTALLED:-0}" != 1 ]; then
    dnf -y install 'golang >= 1.26' tar gzip
fi
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
tar -xzf "$archive" -C "$work"
cd "$work/gomi-$version"
# go.sum verifies module downloads; forbid automatic toolchain downloads.
export GOTOOLCHAIN=local
go mod vendor
# Normalize archive ordering and metadata for reproducible source preparation.
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
    -cf - vendor | gzip -n > "$sources/gomi-$version-deps.tar.gz"
