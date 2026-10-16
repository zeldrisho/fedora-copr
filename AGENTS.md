# Agent Instructions

## Toolchain

- Use Fedora RPM tooling: `rpm-build`, `rpmdevtools`, `rpmlint`, and GNU Make.
- Use Python 3 for repository validation scripts.

## Commands

| Task | Command |
| --- | --- |
| Validate all packages | `scripts/validate.py` |
| Build a package SRPM | `(cd packages/<name> && make -f ../../.copr/Makefile srpm spec=<name>.spec outdir=/tmp/srpms)` |

## Key Conventions

- Keep each Fedora spec at `packages/<name>/<name>.spec`; match directory, spec basename, and `Name:`.
- Keep specs plain and Fedora-submittable; no COPR-only logic or rpkg templates.
- Put COPR-specific behavior only in `.copr/Makefile`.
- Sources must be available when creating the SRPM; Fedora build chroots have no internet access.
- If Fedora documentation cannot be fetched, stop and ask the user to provide a local copy under `docs/`; do not substitute unverified or stale content.

## External References

| Need | File |
| --- | --- |
| End-user installation | `README.md` |
| Development and packaging | `docs/development.md` |
| Toolchain and commands | `docs/toolchain.md` |
| COPR setup | `docs/copr.md` |
