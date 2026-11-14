#!/usr/bin/env bash
# Fast offline negative tests; set VITE_PLUS_ARCHIVE for a networked integration test.
set -euo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/tree/packages/tools"
pins="$work/tree/packages/tools/.upstream-versions.json"

expect_rejected() {
    if "$@" >"$work/log" 2>&1; then
        echo "Unexpected success: $*" >&2
        exit 1
    fi
}

printf 'not an archive\n' > "$work/bad.tar.gz"
expect_rejected bash "$here/prepare-upstream-sources.sh" "$work/bad.tar.gz" "$work/out"
grep -q 'archive checksum mismatch' "$work/log"

# These cases fail before git is invoked, so they never access the network.
python3 - "$pins" <<'PY'
import json
import sys
pins = {
    'rolldown': {'repo': 'https://github.com/rolldown/rolldown.git', 'hash': 'a' * 40},
    'vite': {'repo': 'https://github.com/vitejs/vite.git', 'hash': 'b' * 40},
    'oxc-node': {'repo': 'https://github.com/oxc-project/oxc-node.git', 'hash': 'c' * 40},
}
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    json.dump(pins, f)
PY
cp "$pins" "$work/good.json"
# A minimal valid lockfile lets the offline tests reach the git fetch stage.
python3 - "$work/tree/Cargo.lock" <<'PY'
import sys
sources = [
    ('https://github.com/polachok/passfd', 'a' * 40),
    ('https://github.com/rust-vmm/seccompiler', 'b' * 40),
    ('https://github.com/voidzero-dev/vite-task.git', 'c' * 40),
]
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    for index, (url, commit) in enumerate(sources):
        f.write(f'[[package]]\nname = "test-{index}"\nversion = "1.0.0"\n')
        f.write(f'source = "git+{url}?rev={commit}#{commit}"\n')
PY
cp "$work/tree/Cargo.lock" "$work/good.lock"
# A failed fetch must not publish partial archives or touch existing output.
mkdir -p "$work/bin" "$work/fetch-out"
printf 'keep\n' > "$work/fetch-out/existing"
printf '#!/bin/sh\nexit 1\n' > "$work/bin/git"
chmod +x "$work/bin/git"
expect_rejected env PATH="$work/bin:$PATH" bash "$here/fetch-upstream-sources.sh" "$work/tree" "$work/fetch-out"
test "$(find "$work/fetch-out" -type f | wc -l)" -eq 1
grep -qx keep "$work/fetch-out/existing"
# Reject unreviewed git dependencies and mismatched lockfile revisions before fetching.
printf '\n[[package]]\nname = "bad"\nversion = "1.0.0"\nsource = "git+https://example.invalid/repo?rev=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n' >> "$work/tree/Cargo.lock"
expect_rejected bash "$here/fetch-upstream-sources.sh" "$work/tree" "$work/out"
grep -q 'Unexpected Cargo git source' "$work/log"
cp "$work/good.lock" "$work/tree/Cargo.lock"
python3 - "$pins" <<'PY'
import json
import sys
with open(sys.argv[1], encoding='utf-8') as f:
    pins = json.load(f)
pins['vite']['repo'] = 'https://example.invalid/vite.git'
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    json.dump(pins, f)
PY
expect_rejected bash "$here/fetch-upstream-sources.sh" "$work/tree" "$work/out"
grep -q 'Unexpected repository URL or commit' "$work/log"
cp "$work/good.json" "$pins"
python3 - "$pins" <<'PY'
import json
import sys
with open(sys.argv[1], encoding='utf-8') as f:
    pins = json.load(f)
pins['rolldown']['hash'] = '--upload-pack=evil'
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    json.dump(pins, f)
PY
expect_rejected bash "$here/fetch-upstream-sources.sh" "$work/tree" "$work/out"
grep -q 'Unexpected repository URL or commit' "$work/log"
cp "$work/good.json" "$pins"
python3 - "$pins" <<'PY'
import json
import sys
with open(sys.argv[1], encoding='utf-8') as f:
    pins = json.load(f)
pins['unexpected'] = {}
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    json.dump(pins, f)
PY
expect_rejected bash "$here/fetch-upstream-sources.sh" "$work/tree" "$work/out"
grep -q 'Unexpected upstream repository set' "$work/log"

if [ -n "${VITE_PLUS_ARCHIVE:-}" ]; then
    bash "$here/prepare-upstream-sources.sh" "$VITE_PLUS_ARCHIVE" "$work/first"
    bash "$here/prepare-upstream-sources.sh" "$VITE_PLUS_ARCHIVE" "$work/second"
    (cd "$work/first" && sha256sum ./*.tar.gz) > "$work/checksums"
    (cd "$work/second" && sha256sum -c "$work/checksums")
fi
echo 'Source preparation tests passed'
