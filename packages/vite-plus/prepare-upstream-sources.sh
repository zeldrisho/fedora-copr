#!/usr/bin/env bash
# Verify the known Vite+ release before trusting its external repository pins.
# This is not yet the COPR prepare-sources.sh entry point.
set -euo pipefail
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 VITE_PLUS_ARCHIVE OUTPUT_DIRECTORY" >&2
    exit 2
fi
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
archive=$(realpath "$1")
mkdir -p "$2"
out=$(realpath "$2")
version=$(awk '$1 == "Version:" { print $2; exit }' "$script_dir/vite-plus.spec")
expected=$(awk -v name="v${version}.tar.gz" '$2 == name { print $1 }' "$script_dir/checksums.sha256")
printf '%s  %s\n' "$expected" "$archive" | sha256sum --check --status || {
    echo 'Vite+ archive checksum mismatch' >&2
    exit 1
}
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
tar -xzf "$archive" -C "$work"
test -f "$work/vite-plus-$version/packages/tools/.upstream-versions.json"
bash "$script_dir/fetch-upstream-sources.sh" "$work/vite-plus-$version" "$out"
