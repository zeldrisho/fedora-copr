# Agent Instructions

## Toolchain

- Use Fedora RPM tooling: `rpm-build`, `rpmdevtools`, `rpmlint`, GNU Make, and `copr-cli`.
- Use Python 3 for repository validation scripts.
- Prefer `copr-cli` for COPR status, build, and artifact operations; use HTTP only for information the CLI cannot provide.

## Commands

| Task | Command |
| --- | --- |
| Validate all packages | `scripts/validate.py` |
| Build and retain a package SRPM | `(cd packages/<name> && make -f ../../.copr/Makefile srpm spec=<name>.spec outdir="$HOME/rpmbuild/SRPMS")` |
| List COPR builds | `copr-cli list-builds zeldrisho/packages --output-format json` |
| Download a COPR review | `copr-cli download-build <build-id> -r <chroot> --review --dest dist/review/<name>` |
| Find files and directories | `fd '<pattern>' [path]` |
| Find a local upstream reference | `rg -l -F '<source-url>' docs/` |

## Key Conventions

- Keep each Fedora spec at `packages/<name>/<name>.spec`; match directory, spec basename, and `Name:`.
- Before package changes, consult the relevant repository guidance and package-local spec, README, or maintenance notes for the area being changed; do not reread unrelated documentation for mechanical or unrelated edits. For changes to shared build, validation, or publishing behavior, consult the relevant `.copr/`, CI, and development guidance.
- For new packages, perform an initial local package build and record its duration. For existing packages, choose local builds or COPR based on measured build time and maintenance needs; currently use COPR for Herdr and Yazi binary builds because their local builds take too long. Local SRPM creation and repository validation remain allowed.
- When installing new development or packaging dependencies, update `docs/toolchain.md` with the corresponding local setup instructions so maintainers can reproduce the environment.
- Before creating a spec for a new package, review the relevant local Fedora guidance to determine whether the software is eligible for Fedora and whether its sources and licensing are acceptable. Start with `docs/packaging-guidelines/what-can-be-packaged.md`, then consult applicable packaging and licensing references; resolve eligibility concerns before treating the package as submittable.
- Keep specs plain and Fedora-submittable; no COPR-only logic or rpkg templates.
- In specs, add comments only when useful to Fedora build systems or package maintainers (for example, to explain licensing, offline build/test constraints, source provenance, or non-obvious build workarounds). Avoid comments and markers that are specific to this repository or COPR.
- Put COPR-specific behavior only in `.copr/Makefile`.
- Bump `Release` and add a changelog entry only when a change affects the end-user-facing binary or its behavior (for example, version, installed files, runtime metadata, runtime dependencies, or build flags that change the binary). Do not bump `Release` for source-bundle or build-only changes that do not affect the resulting binary, nor for edits confined to comments, `%check`, `%changelog`, or docs. See `docs/packaging-guidelines/packaging-guidelines.md` (Changelogs).
- Before any local `copr-cli` submission, run `scripts/validate.py` and get it passing; the web `COPR publish` workflow already runs CI first.
- Do not reuse or lower a published Version-Release when the resulting binary package could differ. For a build-only source or packaging change, a published Version-Release may be retained or restored only when the resulting binary RPM is verified to be identical; document the comparison and ensure the build service accepts the matching NVR.
- Sources must be available when creating the SRPM; Fedora build chroots have no internet access.
- For Fedora review submissions, publish the matching SRPM at a public, directly downloadable URL and include that URL in Bugzilla; the SRPM carries the spec and source archives for reviewer inspection. Before inspecting or changing a checked-in source archive (for example, `*.tar.gz` or `*.tar.bz2`), read that package's `README.md` and relevant `docs/` maintenance/audit notes for provenance and regeneration instructions, and inspect the spec's `Source` entries. Keep the archive's checksum manifest (`docs/checksums.sha256`) current and verify it with `sha256sum --check packages/<name>/docs/checksums.sha256` after source changes.
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
