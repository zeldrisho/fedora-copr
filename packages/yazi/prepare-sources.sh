#!/usr/bin/env bash
# Run in COPR's SRPM builder after spectool downloads Source0.
set -euo pipefail
spec=$1
sources=$2
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
archive="$sources/v${version}.tar.gz"

printf '%s  %s\n' "$(<source.sha256)" "$archive" | sha256sum -c -
if [ "${SOURCES_DEPS_PREINSTALLED:-0}" != 1 ]; then
    dnf -y install cargo git tar gzip
fi
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
tar -xzf "$archive" -C "$work"
cd "$work/yazi-$version"
mkdir -p .cargo
# Cargo emits replacements for both crates.io and the locked Git dependency.
cargo vendor --locked --versioned-dirs cargo-vendor > .cargo/config.toml
tar -czf "$sources/yazi-$version-deps.tar.gz" .cargo/config.toml cargo-vendor
