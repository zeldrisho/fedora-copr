#!/usr/bin/env bash
# Verify the upstream npm archive and the pinned OpenPGP.js source before
# creating the SRPM.
set -euo pipefail
sources=$2
(cd "$sources" && sha256sum -c checksums.sha256)
