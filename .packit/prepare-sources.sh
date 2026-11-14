#!/usr/bin/env bash
# Packit create-archive action: leave all RPM sources next to the spec.
set -euo pipefail
package=${1:?package name required}
case "$package" in
    actionlint|gomi|herdr|homebrew|kotlin-toolchain|morphe|pi-coding-agent|rea|smali|vite-plus|yazi) ;;
    *) echo "Unsupported package: $package" >&2; exit 1 ;;
esac
spec="$package.spec"
test -f "$spec" || { echo "Run from packages/$package" >&2; exit 1; }
spectool -g -C . "$spec" >&2
if [ -f prepare-sources.sh ]; then
    SOURCES_DEPS_PREINSTALLED=1 bash ./prepare-sources.sh "$spec" "$PWD" >&2
fi
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
if [ "$package" = kotlin-toolchain ]; then
    archive="kotlin-cli-${version}-wrapper"
elif [ "$package" = rea ]; then
    archive="rea-agents-${version}.tgz"
elif [ "$package" = pi-coding-agent ]; then
    archive="pi-coding-agent-${version}.tgz"
elif [ "$package" = homebrew ] || [ "$package" = smali ]; then
    archive="${version}.tar.gz"
else
    archive="v${version}.tar.gz"
fi
test -f "$archive"
printf '%s\n' "$archive"
