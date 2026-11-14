#!/usr/bin/env bash
# Synchronize already verified source snapshots using upstream's sync logic.
# Run only in a disposable source-preparation environment with network access.
set -euo pipefail
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 VERIFIED_SOURCE_TREE" >&2
    exit 2
fi
root=$(realpath "$1")
cd "$root"
expected_pnpm=$(node -p 'const p = require("./package.json").packageManager; if (!/^pnpm@[0-9]+\.[0-9]+\.[0-9]+$/.test(p)) throw Error("Unsupported packageManager"); p.slice(5)')
[ "$(pnpm --version)" = "$expected_pnpm" ] || { echo "Vite+ requires pnpm $expected_pnpm" >&2; exit 1; }
node -e 'if (Number(process.versions.node.split(".")[0]) < 24) process.exit(1)'
for dir in rolldown vite oxc-node; do
    [ -f "$dir/package.json" ] || { echo "Missing source snapshot: $dir" >&2; exit 1; }
done
# Upstream's branding step restores files from Vite's Git HEAD before patching.
# Create a disposable baseline for the verified archive; never modify an
# existing repository supplied by the caller.
[ ! -e vite/.git ] || { echo 'Expected a Vite snapshot without Git metadata' >&2; exit 1; }
work=$(mktemp -d)
script=packages/tools/src/sync-remote-deps.ts
cp "$script" "$work/original"
sha256sum pnpm-lock.yaml Cargo.lock > "$work/locks"
restore() {
    cp "$work/original" "$root/$script"
    rm -rf "$root/vite/.git" "$work"
}
trap restore EXIT
git -C vite init -q
git -C vite -c core.hooksPath=/dev/null add -f .
git -C vite -c user.name='Vite+ source preparation' -c user.email='nobody@localhost' \
    -c core.hooksPath=/dev/null commit -qm 'Verified Vite snapshot'
# Upstream normally clones and resets mutable branches. The caller has already
# supplied verified snapshots, so only skip this checkout step; keep all of
# upstream's workspace transformations. Fail if the release changes shape.
python3 - "$script" <<'PY'
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
old = '    cloneOrResetRepo(repo, join(rootDir, dir), branch, hash);'
new = '    if (!existsSync(join(rootDir, dir))) throw new Error(`Missing verified snapshot: ${dir}`);'
if text.count(old) != 1:
    raise SystemExit('Unexpected upstream sync implementation')
path.write_text(text.replace(old, new), encoding='utf-8')
PY
node packages/tools/src/index.ts sync-remote
# The release lockfiles are the review boundary for dependency resolution.
sha256sum --check "$work/locks"
