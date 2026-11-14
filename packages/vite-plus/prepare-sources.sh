#!/usr/bin/env bash
# COPR SRPM preparation: fetch Git sources pinned by the verified release.
# The package spec and remaining build dependencies are still under development.
set -euo pipefail
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 SPEC SOURCES_DIRECTORY" >&2
    exit 2
fi
spec=$1
sources=$(realpath "$2")
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
# Packit installs these with srpm_build_deps; standalone runs install them here.
if [ "${SOURCES_DEPS_PREINSTALLED:-0}" != 1 ]; then
    dnf -y install git-core python3 tar gzip
fi
bash "$script_dir/prepare-upstream-sources.sh" "$sources/v$version.tar.gz" "$work/archives"
tar -czf "$sources/vite-plus-$version-git-sources.tar.gz" -C "$work/archives" .
