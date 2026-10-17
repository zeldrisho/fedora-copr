# Agent Instructions

## Toolchain

- Use Fedora RPM tooling: `rpm-build`, `rpmdevtools`, `rpmlint`, and GNU Make.
- Use Python 3 for repository validation scripts.

## Commands

| Task | Command |
| --- | --- |
| Validate all packages | `scripts/validate.py` |
| Build and retain a package SRPM | `(cd packages/<name> && make -f ../../.copr/Makefile srpm spec=<name>.spec outdir="$HOME/rpmbuild/SRPMS")` |
| Find a local upstream reference | `rg -l -F '<source-url>' docs/` |

## Key Conventions

- Keep each Fedora spec at `packages/<name>/<name>.spec`; match directory, spec basename, and `Name:`.
- Before package changes, consult the relevant repository guidance and package-local spec, README, or maintenance notes for the area being changed; do not reread unrelated documentation for mechanical or unrelated edits. For changes to shared build, validation, or publishing behavior, consult the relevant `.copr/`, CI, and development guidance.
- When installing new development or packaging dependencies, update `docs/toolchain.md` with the corresponding local setup instructions so maintainers can reproduce the environment.
- Before creating a spec for a new package, review the relevant local Fedora guidance to determine whether the software is eligible for Fedora and whether its sources and licensing are acceptable. Start with `docs/packaging-guidelines/what-can-be-packaged.md`, then consult applicable packaging and licensing references; resolve eligibility concerns before treating the package as submittable.
- Keep specs plain and Fedora-submittable; no COPR-only logic or rpkg templates.
- Put COPR-specific behavior only in `.copr/Makefile`.
- Bump `Release` and add a changelog entry only for changes users would notice (version, installed files, metadata, dependencies, build flags, sources); skip both for edits confined to comments, `%check`, `%changelog`, or docs. See `docs/packaging-guidelines/packaging-guidelines.md` (Changelogs).
- Never reuse or lower a published Version-Release. A Release reset is allowed only after all prior COPR builds are withdrawn and confirmed not downloaded or installed.
- Sources must be available when creating the SRPM; Fedora build chroots have no internet access.
- Store local Fedora packaging/licensing references under `docs/packaging-guidelines/` and package-maintainer references under `docs/package-maintainers/`; use lowercase, hyphenated filenames and retain each canonical URL in the file.
- Maintain the relevant directory `README.md` index when adding or moving a reference. Before fetching a Fedora document, search `docs/` by canonical URL, verify the matching file's source URL, and read it regardless of filename. Fetch only if no matching copy exists or refresh is explicitly needed.
- Consult COPR documentation at `docs.copr.fedorainfracloud.org` directly; do not treat it as a Fedora reference copy.
- If a needed Fedora document cannot be fetched, stop and ask the user to provide a verified copy. Give the exact repository-relative destination path and a suggested lowercase, hyphenated filename under the appropriate directory: `docs/packaging-guidelines/<suggested-name>.md` or `docs/package-maintainers/<suggested-name>.md`. Do not substitute unverified or stale content.
- Keep package-specific audit/review records, when needed, under `packages/<name>/docs/` with concise names such as `audit.md` and `review.md`.

## External References

| Need | File |
| --- | --- |
| End-user installation | `README.md` |
| Development and packaging | `docs/development.md` |
| Toolchain and commands | `docs/toolchain.md` |
| COPR setup | `docs/copr.md` |
| Fedora packaging guidance | `docs/packaging-guidelines/README.md` |
| Fedora package-maintainer guidance | `docs/package-maintainers/README.md` |
| Fedora submission procedure | `docs/submission.md` |
| Package-specific review/audit records | `packages/<name>/docs/` |
