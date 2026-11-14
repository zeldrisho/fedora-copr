#!/usr/bin/env bash
# Fetch the extra upstream repositories pinned by a verified Vite+ source tree.
# This is a preparation helper, not yet a complete COPR source preparation script.
set -euo pipefail
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 VERIFIED_SOURCE_TREE OUTPUT_DIRECTORY" >&2
    exit 2
fi
source_tree=$(realpath "$1")
mkdir -p "$2"
out=$(realpath "$2")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir "$work/archives"

# Restrict URLs and commit IDs: the input source tree must first be verified
# against an independently maintained digest by the caller.
python3 - "$source_tree/packages/tools/.upstream-versions.json" > "$work/pins" <<'PY'
import json
import re
import sys

with open(sys.argv[1], encoding='utf-8') as f:
    pins = json.load(f)
repositories = {
    'rolldown': 'https://github.com/rolldown/rolldown.git',
    'vite': 'https://github.com/vitejs/vite.git',
    'oxc-node': 'https://github.com/oxc-project/oxc-node.git',
}
if set(pins) != set(repositories):
    raise SystemExit('Unexpected upstream repository set; review before updating')
for name, url in repositories.items():
    entry = pins[name]
    commit = entry.get('hash', '')
    if entry.get('repo') != url or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise SystemExit(f'Unexpected repository URL or commit for {name}')
    print(name, url, commit, sep='\t')
PY

# Cargo's lockfile also names git dependencies. They are not covered by the
# workspace repository pins above; accept only audited upstream repositories
# and require the URL's rev to agree with Cargo's locked commit.
python3 - "$source_tree/Cargo.lock" >> "$work/pins" <<'PY'
import re
import sys
import tomllib
from urllib.parse import parse_qs, urlsplit

repositories = {
    'https://github.com/polachok/passfd': 'cargo-passfd',
    'https://github.com/rust-vmm/seccompiler': 'cargo-seccompiler',
    'https://github.com/voidzero-dev/vite-task.git': 'cargo-vite-task',
}
with open(sys.argv[1], 'rb') as f:
    lock = tomllib.load(f)
found = {}
for package in lock.get('package', []):
    source = package.get('source', '')
    if not source.startswith('git+'):
        continue
    parsed = urlsplit(source[4:])
    url = f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
    query = parse_qs(parsed.query, strict_parsing=True)
    commit = parsed.fragment
    if (url not in repositories or set(query) != {'rev'}
            or query['rev'] != [commit] or not re.fullmatch(r'[0-9a-f]{40}', commit)):
        raise SystemExit(f'Unexpected Cargo git source: {source}')
    name = repositories[url]
    if name in found and found[name] != commit:
        raise SystemExit(f'Multiple revisions of Cargo git source: {url}')
    found[name] = commit
for url, name in repositories.items():
    if name not in found:
        raise SystemExit(f'Missing expected Cargo git source: {url}')
    print(name, url, found[name], sep='\t')
PY

fetch_commit() {
    local name=$1 url=$2 commit=$3
    git init -q "$work/$name"
    git -C "$work/$name" -c protocol.file.allow=never fetch -q --depth=1 "$url" "$commit"
    test "$(git -C "$work/$name" rev-parse 'FETCH_HEAD^{commit}')" = "$commit"
}

while IFS=$'\t' read -r name url commit; do
    fetch_commit "$name" "$url" "$commit"
    git -C "$work/$name" ls-tree -r "$commit" > "$work/$name.tree"
    while IFS=$'\t' read -r metadata path; do
        [[ "$metadata" == 160000\ commit\ * ]] || continue
        subcommit=${metadata##* }
        # The URL comes from this allowlist, not from a mutable .gitmodules.
        case "$name/$path" in
            rolldown/rollup) suburl=https://github.com/rollup/rollup.git ;;
            rolldown/test262) suburl=https://github.com/tc39/test262.git ;;
            cargo-seccompiler/rust-vmm-ci) suburl=https://github.com/rust-vmm/rust-vmm-ci.git ;;
            cargo-vite-task/crates/fspy_detours_sys/detours) suburl=https://github.com/microsoft/Detours.git ;;
            *) echo "Unexpected submodule: $name/$path" >&2; exit 1 ;;
        esac
        subname="$name-${path//\//-}"
        fetch_commit "$subname" "$suburl" "$subcommit"
        if git -C "$work/$subname" ls-tree -r "$subcommit" | grep -q '^160000 '; then
            echo "Nested submodules require review: $name/$path" >&2
            exit 1
        fi
        git -C "$work/$subname" archive --format=tar --prefix="$name/$path/" "$subcommit" > "$work/$subname.tar"
        gzip -n < "$work/$subname.tar" > "$work/archives/$subname-$subcommit.tar.gz"
    done < "$work/$name.tree"
    git -C "$work/$name" archive --format=tar --prefix="$name/" "$commit" > "$work/$name.tar"
    gzip -n < "$work/$name.tar" > "$work/archives/$name-$commit.tar.gz"
done < "$work/pins"
# Do not publish partial output when a later fetch fails.
cp -a "$work/archives/." "$out/"
