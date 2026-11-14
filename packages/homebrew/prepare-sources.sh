#!/usr/bin/env bash
set -euo pipefail
spec=$1
sources=$2
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$spec")
printf '%s  %s\n' "$(<source.sha256)" "$sources/$version.tar.gz" | sha256sum -c -
