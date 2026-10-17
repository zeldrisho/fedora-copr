# Package development

This guide describes how to maintain packages in this repository. For local setup and commands, see the [toolchain guide](toolchain.md). Consult the [Fedora packaging references](packaging-guidelines/README.md) and [package-maintainer references](package-maintainers/README.md) for Fedora guidance relevant to the package being changed.

## Repository layout

```text
.copr/                  Shared SRPM preparation and COPR project metadata
.github/workflows/      Pull-request validation and main-branch publishing
packages/<name>/        Fedora spec and package-specific sources/docs
scripts/                Repository validation helpers
tests/                  Python tests for repository helpers
docs/                   Shared development, packaging, and Fedora guidance
```

GitHub Actions validates pull requests and publishes successful pushes to `main`. CI checks EVR increases, creates and lints SRPMs, and builds binary RPMs locally in Fedora; pull requests do not receive COPR credentials or submit builds. After a validated push to `main`, a separate job synchronizes SCM recipes and submits builds only for packages with changed build inputs. For validation, changes to shared build/CI tooling select every package. For COPR submission, only changes under `.copr/` do, because nothing else alters a package's contents; package README or `docs/`-only changes select none. COPR's configured chroots remain authoritative for published builds.

Every package lives in `packages/<name>/` and uses `packages/<name>/<name>.spec`; the directory, spec basename, and RPM `Name:` must match. Keep specs Fedora-submittable and COPR-specific behavior in `.copr/Makefile`. Put package-specific sources and maintenance notes alongside the spec. Check [actionlint's package notes](../packages/actionlint/README.md) before changing its checked-in Go vendor archive.

## Updating a package

1. Review the upstream release, source integrity (including upstream signatures when available), Fedora-allowed licensing, dependencies, and Fedora compatibility. See the [Fedora packaging references](packaging-guidelines/README.md).
2. Update `Version`, source declarations, patches, build requirements, and package documentation as needed. Regenerate checked-in vendored sources when required and keep them synchronized with the spec.
3. Use explicit `Version` and `Release` fields with a maintained `%changelog`; this repository's COPR SRPM flow does not process `%autorelease` or `%autochangelog`. rpmautospec cannot work in this monorepo: it opens the git repository at the spec's own directory without searching parents, so for `packages/<name>/` it finds no history and would always produce Release 1 and a generic changelog entry. Sign changelog entries as `Zeldris <zeldrisho@proton.me>`. Fedora recommends `%autochangelog` (manual changelogs are allowed), so switch to `%autorelease` and `%autochangelog` when the package moves to Fedora dist-git, where the first commit message becomes the initial changelog entry.
4. Ensure all sources are available when creating the SRPM. Binary RPM builds must work offline; do not fetch sources or Go modules during build or test phases. Keep `%check` deterministic and offline. Document and narrowly skip tests that require network access or unavailable release metadata.
5. For changes to an existing package that users would notice (version, installed files, metadata, dependencies, build flags, patches or other sources), increment `Release` and add a changelog entry. Do not bump for packager-only changes: edits confined to comments, `%check`, or `%changelog`, documentation, or COPR configuration. The EVR checker ignores package README files and files under package `docs/` directories; those documentation-only changes do not require an EVR bump. It skips a spec-only change when everything outside comments, `%check` and `%changelog` is unchanged. To correct an initial release without bumping, keep `Release: 1` only if all prior COPR builds have been withdrawn and confirmed not downloaded or installed, and add the exact `Initial release reset: all prior COPR builds withdrawn and confirmed not downloaded or installed` changelog line in that change; the checker accepts it only for the same `Version` and only when the line is new, and it can be removed afterward.
6. Run `make validate`, then build and review a binary RPM as described in the [toolchain guide](toolchain.md). Lint the SRPM and every binary RPM; inspect metadata, dependencies, provides, files, and license files; and smoke-test an installed command where practical. `make validate` does not perform binary RPM checks and removes its temporary artifacts when it exits. To retain an SRPM or build outputs, use the persistent-output commands in the [toolchain guide](toolchain.md).

Pull-request CI checks that RPM considers the new Version-Release greater than the merge-base value. The checker permits a reset to Release 1 for the same Version only when the current spec contains the exact initial-release reset marker above and the base spec does not, so the marker authorizes a single reset, documenting that all earlier COPR builds were withdrawn and confirmed not downloaded or installed. Never reuse a version-release that has been published with different package contents.

## Build and publish

After merge, inspect the COPR build across its configured chroots; the local CI build does not replace those target builds. See [COPR setup](copr.md) for publishing details.

For submission to the official Fedora repositories, follow the [submission guide](submission.md) and use the [review template](templates/review.md). Keep package-specific review records under `packages/<name>/docs/`. COPR publication alone does not submit a Fedora package review.
