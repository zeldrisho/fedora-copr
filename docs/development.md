# Package development

This guide describes how to maintain packages in this repository. For Fedora's package-submission process, see the [Fedora new-package process](fedora-new-package-process.md). For local setup and commands, see the [toolchain guide](toolchain.md).

## Repository layout

```text
.copr/                  Shared SRPM preparation and COPR project metadata
.github/workflows/      Pull-request validation and main-branch publishing
packages/<name>/        Fedora spec and package-specific sources/docs
scripts/                Repository validation helpers
tests/                  Python tests for repository helpers
docs/                   Development, toolchain, COPR, and upstream guides
```

GitHub Actions validates pull requests and publishes successful pushes to `main`. Pull-request CI creates an SRPM, checks it with rpmlint, and builds the binary RPM locally in Fedora; it does not expose COPR credentials or submit PR builds. After a validated push to `main`, a separate job synchronizes the COPR SCM recipe and submits the build. COPR's configured chroots remain authoritative for published builds.

Every package uses `packages/<name>/<name>.spec`, with the directory, spec basename, and RPM `Name:` aligned. Keep specs Fedora-submittable and COPR-specific behavior in `.copr/Makefile`.

## Package structure

Each package lives in `packages/<name>/` and has a matching `packages/<name>/<name>.spec`. Keep the spec's `Name:` consistent with both. Put package-specific sources and maintenance notes alongside the spec.

Specs must remain Fedora-submittable. Keep COPR behavior in `.copr/Makefile`, not in package specs. Check [actionlint's package notes](../packages/actionlint/README.md) before changing its checked-in Go vendor archive.

## Updating a package

1. Review the upstream release, source integrity, licensing, dependencies, and Fedora compatibility.
2. Update `Version`, source declarations, patches, build requirements, and package documentation as needed. Regenerate checked-in vendored sources when required and keep them synchronized with the spec.
3. Use explicit `Version` and `Release` fields with a maintained `%changelog`; this repository's COPR SRPM flow does not process `%autorelease` or `%autochangelog`.
4. Ensure all sources are available when creating the SRPM. Binary RPM builds must work offline; do not fetch sources or Go modules during build or test phases. Keep `%check` deterministic and offline. Document and narrowly skip tests that require network access or unavailable release metadata.
5. For build-relevant changes to an existing package, increment `Release` and add a changelog entry. Do not bump for documentation-only changes or COPR configuration alone.
6. Run `make validate`, then build and review a binary RPM as described in the [toolchain guide](toolchain.md). Check its metadata and files, and smoke-test the installed command where practical.

Pull-request CI checks that RPM considers the new Version-Release greater than the merge-base value. The one-time exception is a documented reset to Release 1 when all earlier COPR builds failed before publishing; the checker requires the matching changelog note. Never reuse a version-release that has been published with different package contents.

## Build and publish

After merge, inspect the COPR build across its configured chroots; the local CI build does not replace those target builds. See [COPR setup](copr.md) for publishing details.
