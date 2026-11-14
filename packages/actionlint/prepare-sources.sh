#!/usr/bin/env bash
# Run in COPR's SRPM builder after spectool downloads Source0.
set -euo pipefail
spec=$1
sources=$2
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
archive="$sources/v${version}.tar.gz"

printf '%s  %s\n' "$(<source.sha256)" "$archive" | sha256sum -c -
if [ "${SOURCES_DEPS_PREINSTALLED:-0}" != 1 ]; then
    dnf -y install 'golang >= 1.25' tar gzip
fi
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
tar -xzf "$archive" -C "$work"
cd "$work/actionlint-$version"
# go.sum verifies module downloads; forbid automatic toolchain downloads.
export GOTOOLCHAIN=local
go mod vendor
tar -czf "$sources/actionlint-$version-deps.tar.gz" vendor
