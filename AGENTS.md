# Agent Instructions

## Toolchain

- Use Fedora RPM tooling: `rpm-build`, `rpmdevtools`, `rpmlint`, and GNU Make.
- Use Python 3 for repository validation scripts.

## Commands

| Task | Command |
| --- | --- |
| Validate all packages | `scripts/validate.py` |
| Build a package SRPM | `(cd packages/<name> && make -f ../../.copr/Makefile srpm spec=<name>.spec outdir=/tmp/srpms)` |
| Find a local upstream reference | `rg -l -F '<source-url>' docs/upstream/` |

## Key Conventions

- Keep each Fedora spec at `packages/<name>/<name>.spec`; match directory, spec basename, and `Name:`.
- Keep specs plain and Fedora-submittable; no COPR-only logic or rpkg templates.
- Put COPR-specific behavior only in `.copr/Makefile`.
- Bump `Release` and add a changelog entry only for build-relevant package changes; do not include packager-only changes that do not affect binary package contents. See `docs/upstream/packaging-guidelines.md` (Changelogs).
- Never reuse or lower a published Version-Release. A Release reset is allowed only after all prior COPR builds are withdrawn and confirmed not downloaded or installed.
- Sources must be available when creating the SRPM; Fedora build chroots have no internet access.
- Use `docs/upstream/` for local copies of Fedora packaging and licensing documentation sourced from `docs.fedoraproject.org`; record each canonical URL in the file.
- Before fetching a Fedora document for a local copy, search `docs/upstream/` by its canonical URL, verify the matching file's source URL, and read it regardless of filename. Fetch only when no matching copy exists or a refresh is explicitly needed.
- COPR documentation is published at `docs.copr.fedorainfracloud.org`; consult/fetch it directly when needed and do not treat it as a `docs/upstream/` Fedora document copy.
- Keep local Fedora references focused on packaging guidelines and licensing; do not fetch or add `package-maintainers` documentation unless the user explicitly expands the project scope.
- If a needed Fedora document cannot be fetched, stop and ask the user to provide a verified copy under `docs/upstream/`; do not substitute unverified or stale content.

## External References

| Need | File |
| --- | --- |
| End-user installation | `README.md` |
| Development and packaging | `docs/development.md` |
| Toolchain and commands | `docs/toolchain.md` |
| COPR setup | `docs/copr.md` |
| Upstream packaging references | `docs/upstream/` (find by source URL) |
