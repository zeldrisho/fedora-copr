#!/usr/bin/env bash
# Run in COPR's SRPM builder after spectool downloads Source0.
set -euo pipefail
spec=$1
sources=$2
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
archive="$sources/v${version}.tar.gz"

if [ "${SOURCES_DEPS_PREINSTALLED:-0}" != 1 ]; then
    dnf -y install cargo zig tar gzip
fi
[ "$(zig version)" = 0.16.0 ] || { echo 'Herdr requires Zig 0.16.0' >&2; exit 1; }
printf '%s  %s\n' "$(<source.sha256)" "$archive" | sha256sum -c -
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
tar -xzf "$archive" -C "$work"
cd "$work/herdr-$version"
mkdir -p .cargo
cargo vendor --locked --versioned-dirs cargo-vendor > .cargo/config.toml
export ZIG_GLOBAL_CACHE_DIR="$PWD/zig-global-cache"
(cd vendor/libghostty-vt && zig build --fetch=all)
tar -czf "$sources/herdr-$version-deps.tar.gz" .cargo/config.toml cargo-vendor zig-global-cache
