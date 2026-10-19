# Package development

This guide describes how to maintain packages in this repository. For local setup and commands, see the [toolchain guide](toolchain.md). Use the [Fedora reference links](references.md) for current policy and submission guidance.

## Repository layout

```text
.copr/                  Shared SRPM preparation and COPR project metadata
.github/workflows/      Validation and manual COPR publishing
packages/<name>/        Fedora spec and package-specific sources/docs
scripts/                Repository validation helpers
tests/                  Python tests for repository helpers
docs/                   Shared development, packaging, and Fedora guidance
```

GitHub Actions validates relevant pull requests and pushes to `main`: it runs repository tests, checks package EVR increases, verifies source-checksum manifests, and validates/lints package SRPMs. Yazi filter-helper tests run when that helper changes. Root/shared documentation-only changes do not trigger CI; changes under `packages/` do. CI has no COPR credentials and does not build binary RPMs. Publishing is manual; COPR builds run asynchronously. Review COPR results and inspect/smoke-test binaries using the [toolchain guide](toolchain.md). The upstream-check workflow reports newer stable releases but never updates packages.

Every package lives in `packages/<name>/` and uses `packages/<name>/<name>.spec`; the directory, spec basename, and RPM `Name:` must match. Keep specs Fedora-submittable and COPR-specific behavior in `.copr/Makefile`. Package source archives live alongside the spec; their `Source` declarations show how builds consume them. Before changing an archive, read that package's `README.md` and relevant `docs/` notes for provenance and regeneration steps, then verify the package's `docs/checksums.sha256` manifest after the change. For example, see [actionlint's package notes](../packages/actionlint/README.md), [Herdr's notes](../packages/herdr/README.md), and [Yazi's notes](../packages/yazi/README.md). For Fedora review submissions, publish the matching SRPM at a public, directly downloadable URL and include that URL in Bugzilla; the SRPM contains the spec and required source archives for the reviewer.

## Updating a package

1. Review the upstream release, source integrity (including upstream signatures when available), Fedora-allowed licensing, dependencies, and Fedora compatibility. See the current [Fedora packaging references](references.md).
2. Update `Version`, source declarations, patches, build requirements, and package documentation as needed. Regenerate checked-in vendored sources when required and keep them synchronized with the spec.
3. Use explicit `Version` and `Release` fields with a maintained `%changelog`; this repository's COPR SRPM flow does not process `%autorelease` or `%autochangelog`. rpmautospec cannot work in this monorepo: it opens the git repository at the spec's own directory without searching parents, so for `packages/<name>/` it finds no history and would always produce Release 1 and a generic changelog entry. Sign changelog entries as `Zeldris Ho <zeldrisho@proton.me>`. Fedora recommends `%autochangelog` (manual changelogs are allowed), so switch to `%autorelease` and `%autochangelog` when the package moves to Fedora dist-git, where the first commit message becomes the initial changelog entry.
4. Ensure all sources are available when creating the SRPM. Binary RPM builds must work offline; do not fetch sources or Go modules during build or test phases. Keep `%check` deterministic and offline. Document and narrowly skip tests that require network access or unavailable release metadata.
5. Apply the [EVR and changelog policy](#version-release-and-changelog) when changing an existing package.
6. Run `make validate`, then build and review a binary RPM as described in the [toolchain guide](toolchain.md). For a new package, perform an initial local package build and record elapsed time; use that measurement to decide whether later builds stay local or move to COPR. For existing packages, choose based on measured build time and maintenance needs (current Herdr and Yazi binary builds use COPR because local builds take too long). Lint the SRPM and every binary RPM; inspect metadata, dependencies, provides, files, and license files; and smoke-test an installed command where practical. `make validate` does not perform binary RPM checks and removes its temporary artifacts when it exits. To retain an SRPM or build outputs, use the persistent-output commands in the [toolchain guide](toolchain.md).

## Version, release, and changelog

For changes affecting the packaged executable or behavior, increment `Release` and add a changelog entry. Do not bump for docs, comments, `%check`, or build-only changes that do not change the RPM. Never reuse a published NVR if RPM contents could differ, including license or documentation payload changes.

CI checks that RPM considers the new EVR greater than the merge-base value. The checker ignores package README/docs-only changes, certain test-only `BuildRequires`, and removal of a checked-in source cache when the spec declares that source remotely; modifications or additions to source archives still require an EVR increase. A Release 1 reset for the same Version is accepted only with the exact marker `Initial release reset: all prior COPR builds withdrawn and confirmed not downloaded or installed`, and only when prior builds were actually withdrawn and confirmed not installed. See the checker for its precise conditions.

## Build and publish

Publish manually (see COPR setup), then inspect the COPR build across its configured chroots; the local CI build does not replace those target builds. See [COPR setup](copr.md) for publishing details.

For submission to the official Fedora repositories, follow the [submission guide](submission.md) and use the [review template](templates/review.md). Keep package-specific review records under `packages/<name>/docs/`. COPR publication alone does not submit a Fedora package review.
