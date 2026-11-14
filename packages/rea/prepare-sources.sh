#!/usr/bin/env bash
# Verify the upstream npm archive before creating the SRPM.
set -euo pipefail
version=$(rpmspec -q --srpm --qf '%{VERSION}' "$1")
printf '%s  %s\n' "$(<source.sha256)" "$2/rea-agents-${version}.tgz" | sha256sum -c -
