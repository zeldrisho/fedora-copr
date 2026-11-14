#!/usr/bin/env bash
# Verify upstream inputs before creating the SRPM. npm resolves dependencies
# during the network-enabled RPM build.
set -euo pipefail
sources=$2
(cd "$sources" && sha256sum -c checksums.sha256)
