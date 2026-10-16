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
- Never reuse or lower a published Version-Release; a Release reset is allowed only when all earlier builds failed before publishing.
- Sources must be available when creating the SRPM; Fedora build chroots have no internet access.
- Keep upstream documentation copies under `docs/upstream/`, with their canonical source URL in each file.
- Before fetching upstream documentation, search locally by URL, verify the matching file's source URL, and read it regardless of filename.
- Fetch only when no matching local copy exists or a refresh is explicitly needed.
- Keep local upstream references focused on packaging guidelines and COPR; do not fetch or add `package-maintainers` documentation unless the user explicitly expands the project scope.
- If needed Fedora documentation cannot be fetched, stop and ask the user to provide a local copy under `docs/upstream/`; do not substitute unverified or stale content.

## External References

| Need | File |
| --- | --- |
| End-user installation | `README.md` |
| Development and packaging | `docs/development.md` |
| Toolchain and commands | `docs/toolchain.md` |
| COPR setup | `docs/copr.md` |
| Upstream packaging references | `docs/upstream/` (find by source URL) |
