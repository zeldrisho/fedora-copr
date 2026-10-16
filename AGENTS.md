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

## External References

| Need | File |
| --- | --- |
| End-user installation | `README.md` |
| Development and COPR setup | `docs/development.md` |
| Fedora packaging policy notes | `docs/fedora-packaging.md` |
