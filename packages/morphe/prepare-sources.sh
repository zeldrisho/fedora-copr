#!/usr/bin/env bash
# Verify upstream archives before creating the SRPM.
set -euo pipefail
(cd "$2" && sha256sum -c checksums.sha256)
